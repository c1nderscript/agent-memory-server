export interface DormantMCPServer {
  start(): Promise<void>;
  stop(): Promise<void>;
  activate(): Promise<void>;
  deactivate(): Promise<void>;
}

import { EventEmitter } from "events";
import { createServer, Server as HttpServer, IncomingMessage, ServerResponse } from "http";
import { createServer as createNetServer, Server as NetServer } from "net";
import os from "os";

export class DefaultDormantMCPServer extends EventEmitter implements DormantMCPServer {
  private httpServer: HttpServer | null = null;
  private activationServer: NetServer | null = null;
  private active = false;
  private shutdownTimer?: NodeJS.Timeout;
  private monitorInterval?: NodeJS.Timeout;

  constructor(
    private readonly port: number = 9000,
    private readonly activationPort: number = 9100,
    private readonly inactivityMs: number = 300_000
  ) {
    super();
  }

  async start(): Promise<void> {
    this.httpServer = createServer(this.handleRequest.bind(this));
    await new Promise<void>((resolve) => {
      this.httpServer!.listen(this.port, resolve);
    });

    this.activationServer = createNetServer((socket) => {
      socket.on("data", () => this.activate());
    });
    await new Promise<void>((resolve) => {
      this.activationServer!.listen(this.activationPort, resolve);
    });

    process.on("SIGUSR1", () => this.activate());
    process.on("SIGINT", () => this.stop());
    process.on("SIGTERM", () => this.stop());

    this.startResourceMonitor();
    this.scheduleShutdown();
  }

  private async handleRequest(req: IncomingMessage, res: ServerResponse) {
    this.activate();
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok" }));
  }

  async activate(): Promise<void> {
    if (this.active) {
      this.scheduleShutdown();
      return;
    }
    this.active = true;
    this.emit("activated");
    this.scheduleShutdown();
  }

  async deactivate(): Promise<void> {
    if (!this.active) return;
    this.active = false;
    this.emit("deactivated");
  }

  private scheduleShutdown() {
    if (this.shutdownTimer) clearTimeout(this.shutdownTimer);
    this.shutdownTimer = setTimeout(() => {
      this.deactivate();
      this.stop();
    }, this.inactivityMs);
  }

  async stop(): Promise<void> {
    if (this.httpServer) {
      await new Promise<void>((resolve) => this.httpServer!.close(() => resolve()));
      this.httpServer = null;
    }
    if (this.activationServer) {
      await new Promise<void>((resolve) => this.activationServer!.close(() => resolve()));
      this.activationServer = null;
    }
    this.stopResourceMonitor();
    this.emit("stopped");
  }

  private startResourceMonitor() {
    this.monitorInterval = setInterval(() => {
      const memoryMb = Math.round(process.memoryUsage().rss / 1024 / 1024);
      const cpuLoad = os.loadavg()[0];
      const usage = { memory_mb: memoryMb, cpu_load: cpuLoad };
      console.error(JSON.stringify({ type: "resources", usage }));
    }, 10000);
  }

  private stopResourceMonitor() {
    if (this.monitorInterval) clearInterval(this.monitorInterval);
  }
}

export default DefaultDormantMCPServer;
