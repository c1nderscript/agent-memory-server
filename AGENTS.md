# Redis Agent Memory Server - Warp Terminal Fork

## Project Overview

This is a specialized fork of the Redis Agent Memory Server, re-architected specifically for Warp terminal agent integration. The system provides sophisticated memory management capabilities for AI agents through Redis-backed storage, semantic search, and automatic summarization. Unlike the original implementation designed for Claude/Cursor, this fork optimizes for terminal-based agent workflows with enhanced CLI interfaces and streamlined terminal integration.

## Technology Stack

- **Backend Framework**: FastAPI with Python 3.9+
- **Memory Store**: Redis Stack with RediSearch
- **Vector Databases**: Multiple backends (Redis, Chroma, Pinecone, Weaviate, Qdrant, Milvus, PostgreSQL/PGVector, LanceDB, OpenSearch)
- **Authentication**: OAuth2/JWT Bearer tokens (Auth0, AWS Cognito, Okta, Azure AD)
- **CLI Framework**: Click for command-line interface
- **Background Tasks**: Celery with Redis broker
- **API Documentation**: OpenAPI/Swagger with FastAPI automatic generation
- **Testing**: pytest with coverage reporting
- **Deployment**: Docker containers with docker-compose orchestration

## Project Structure

```
redis-agent-memory-server/
├── src/
│   ├── agents/                 # Warp terminal agent integrations
│   │   ├── __init__.py
│   │   ├── base_agent.py      # Base agent class for Warp integration
│   │   ├── memory_agent.py    # Memory management agent
│   │   ├── search_agent.py    # Semantic search agent
│   │   └── task_agent.py      # Background task management agent
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   ├── routers/          # API route definitions
│   │   ├── models/           # Pydantic models
│   │   └── dependencies.py   # Dependency injection
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration management
│   │   ├── database.py       # Redis connection management
│   │   ├── auth.py           # OAuth2/JWT authentication
│   │   └── vector_stores.py  # Vector database abstractions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── memory_service.py # Memory operations
│   │   ├── search_service.py # Semantic search
│   │   └── task_service.py   # Background task management
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py           # CLI entry point
│   │   ├── commands/         # Command implementations
│   │   └── warp_integration.py # Warp-specific utilities
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── warp_agents/      # Warp agent-specific tests
├── docs/
│   ├── warp/
│   │   └── warp-integration.md   # Warp terminal integration guide
│   ├── api.md               # API documentation
│   └── deployment.md        # Deployment guide
├── scripts/
│   ├── setup.sh             # Environment setup
│   ├── start_warp_agents.sh # Warp agent startup
│   └── health_check.sh      # System health verification
├── config/
│   ├── .env.example
│   ├── redis.conf
│   └── warp_agents.yaml     # Warp agent configuration
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── warp-agents.dockerfile
├── requirements.txt
├── setup.py
├── pyproject.toml
└── README.md
```

## Development Guidelines

### Warp Terminal Agent Integration Standards

- **Agent Architecture**: All agents inherit from `BaseAgent` class with standardized interfaces
- **Terminal Output**: Use structured logging with JSON format for machine parsing
- **Command Patterns**: Implement consistent command-line interface using Click decorators
- **Error Handling**: Provide meaningful error messages with suggested remediation steps
- **Configuration**: Use environment variables with sensible defaults for terminal environments

### Code Style Requirements

- **PEP 8 Compliance**: Strict adherence to Python style guidelines
- **Type Hints**: Mandatory for all function signatures and class attributes
- **Docstrings**: Google-style docstrings for all public methods
- **Import Organization**: Use isort with black-compatible settings
- **Line Length**: 88 characters maximum (black formatter compatible)

### Naming Conventions

- **Files**: snake_case for Python files, kebab-case for shell scripts
- **Classes**: PascalCase (e.g., `MemoryAgent`, `SearchAgent`)
- **Functions**: snake_case with descriptive names
- **Variables**: snake_case with meaningful names
- **Constants**: UPPER_SNAKE_CASE
- **Agents**: Suffix with "Agent" (e.g., `WarpMemoryAgent`)

### Git Workflow

- **Branch Naming**: `feature/agent-name`, `bugfix/issue-description`, `hotfix/critical-fix`
- **Commit Messages**: Conventional commits format with agent-specific prefixes
- **Pull Requests**: Required reviews, automated testing, coverage checks
- **Tagging**: Semantic versioning for releases

## Warp Agent Configuration

### Agent Specifications

#### Memory Agent
```python
class WarpMemoryAgent(BaseAgent):
    """
    Manages working memory and long-term memory operations for Warp terminal integration.
    
    Capabilities:
    - Session-scoped message storage
    - Automatic conversation summarization
    - Memory promotion to long-term storage
    - Context window management
    """
    
    def __init__(self, redis_client, vector_store, config):
        super().__init__(agent_id="warp-memory", config=config)
        self.redis_client = redis_client
        self.vector_store = vector_store
        
    async def store_memory(self, session_id: str, memory_data: dict) -> str:
        """Store memory with automatic categorization"""
        
    async def retrieve_context(self, session_id: str, query: str) -> dict:
        """Retrieve relevant context for terminal commands"""
        
    async def summarize_session(self, session_id: str) -> str:
        """Create session summary when context window exceeded"""
```

#### Search Agent
```python
class WarpSearchAgent(BaseAgent):
    """
    Provides semantic search capabilities optimized for terminal interactions.
    
    Capabilities:
    - Semantic similarity search
    - Filter-based queries
    - Command history search
    - Context-aware suggestions
    """
    
    async def semantic_search(self, query: str, filters: dict = None) -> list:
        """Perform semantic search with terminal-friendly output"""
        
    async def command_history_search(self, session_id: str, pattern: str) -> list:
        """Search command history with fuzzy matching"""
        
    async def suggest_completions(self, partial_command: str, context: dict) -> list:
        """Provide command completions based on context"""
```

#### Task Agent
```python
class WarpTaskAgent(BaseAgent):
    """
    Manages background tasks and job scheduling for terminal operations.
    
    Capabilities:
    - Async task execution
    - Job queue management
    - Progress tracking
    - Result caching
    """
    
    async def schedule_task(self, task_type: str, params: dict) -> str:
        """Schedule background task with terminal progress updates"""
        
    async def get_task_status(self, task_id: str) -> dict:
        """Get task status with terminal-friendly formatting"""
        
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel running task with cleanup"""
```

### Agent Communication Protocol

```yaml
# warp_agents.yaml
agents:
  memory_agent:
    class: "WarpMemoryAgent"
    config:
      session_timeout: 3600
      max_context_window: 4000
      auto_summarize: true
      
  search_agent:
    class: "WarpSearchAgent"
    config:
      similarity_threshold: 0.7
      max_results: 10
      enable_fuzzy_search: true
      
  task_agent:
    class: "WarpTaskAgent"
    config:
      max_concurrent_tasks: 5
      task_timeout: 1800
      enable_progress_tracking: true

communication:
  message_format: "json"
  error_handling: "graceful_degradation"
  logging_level: "INFO"
```

## Environment Setup

### Development Requirements

- **Python**: 3.9 or higher
- **Redis**: 7.0+ with RediSearch module
- **Docker**: 20.10+ for containerized deployment
- **Warp Terminal**: Latest version with agent support
- **Node.js**: 16+ (for frontend assets if needed)

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/redis-agent-memory-server-warp.git
cd redis-agent-memory-server-warp

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -e .

# 4. Set up environment variables
cp config/.env.example .env
# Edit .env with your configuration

# 5. Start Redis with RediSearch
docker-compose up -d redis

# 6. Run database migrations
python -m alembic upgrade head

# 7. Start the FastAPI server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 8. Start Warp agents
./scripts/start_warp_agents.sh

# 9. Verify installation
python -m pytest tests/integration/test_warp_agents.py
```

### Codex Setup Script

A convenience script is provided to automate these steps for Codex agents.
Run `./scripts/setup.sh` to install dependencies, copy the `.env` template,
and set up pre-commit hooks. Keep this script up to date with any
environment changes.

### Environment Variables

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# Vector Store Configuration
VECTOR_STORE_TYPE=redis  # Options: redis, chroma, pinecone, weaviate, qdrant
VECTOR_STORE_URL=redis://localhost:6379
VECTOR_DIMENSION=1536

# Authentication
AUTH_PROVIDER=auth0  # Options: auth0, cognito, okta, azure_ad
AUTH_DOMAIN=your-domain.auth0.com
AUTH_CLIENT_ID=your_client_id
AUTH_CLIENT_SECRET=your_client_secret

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1
DEBUG=false

# Warp Agent Configuration
WARP_AGENT_MODE=true
WARP_SESSION_TIMEOUT=3600
WARP_MAX_CONTEXT_WINDOW=4000
WARP_ENABLE_AUTO_SUMMARIZE=true

# Background Tasks
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/redis-agent-memory-server.log
```

## Core Feature Implementation

### Warp Terminal Integration

```python
# src/cli/warp_integration.py
import click
import asyncio
from typing import Dict, Any
from src.agents.memory_agent import WarpMemoryAgent
from src.agents.search_agent import WarpSearchAgent
from src.agents.task_agent import WarpTaskAgent

class WarpIntegration:
    """
    Main integration class for Warp terminal agent functionality.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents = {}
        self.session_id = None
        
    async def initialize_agents(self):
        """Initialize all Warp agents"""
        self.agents['memory'] = WarpMemoryAgent(
            redis_client=self.redis_client,
            vector_store=self.vector_store,
            config=self.config['agents']['memory_agent']
        )
        
        self.agents['search'] = WarpSearchAgent(
            vector_store=self.vector_store,
            config=self.config['agents']['search_agent']
        )
        
        self.agents['task'] = WarpTaskAgent(
            celery_app=self.celery_app,
            config=self.config['agents']['task_agent']
        )
        
    async def handle_terminal_command(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process terminal commands through appropriate agents"""
        
        # Store command in working memory
        await self.agents['memory'].store_memory(
            session_id=self.session_id,
            memory_data={
                'type': 'command',
                'content': command,
                'context': context,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        # Retrieve relevant context
        relevant_context = await self.agents['memory'].retrieve_context(
            session_id=self.session_id,
            query=command
        )
        
        # Process command based on type
        if command.startswith('search'):
            return await self._handle_search_command(command, relevant_context)
        elif command.startswith('task'):
            return await self._handle_task_command(command, relevant_context)
        else:
            return await self._handle_generic_command(command, relevant_context)
```

### Memory Management

```python
# src/services/memory_service.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.core.database import get_redis_client
from src.core.vector_stores import get_vector_store

class MemoryService:
    """
    Enhanced memory service for Warp terminal integration.
    """
    
    def __init__(self, redis_client, vector_store):
        self.redis = redis_client
        self.vector_store = vector_store
        
    async def store_working_memory(
        self, 
        session_id: str, 
        memory_data: Dict[str, Any]
    ) -> str:
        """Store working memory with automatic context management"""
        
        # Check context window size
        context_size = await self._get_context_window_size(session_id)
        
        if context_size >= self.config.max_context_window:
            # Trigger summarization
            await self._summarize_and_compact(session_id)
            
        # Store new memory
        memory_id = f"{session_id}:{datetime.utcnow().timestamp()}"
        
        await self.redis.hset(
            f"working_memory:{session_id}",
            memory_id,
            json.dumps(memory_data)
        )
        
        # Add to vector store for semantic search
        await self.vector_store.add_document(
            document_id=memory_id,
            content=memory_data.get('content', ''),
            metadata={
                'session_id': session_id,
                'type': memory_data.get('type', 'general'),
                'timestamp': memory_data.get('timestamp'),
                'context': memory_data.get('context', {})
            }
        )
        
        return memory_id
        
    async def retrieve_context(
        self, 
        session_id: str, 
        query: str, 
        max_results: int = 10
    ) -> Dict[str, Any]:
        """Retrieve relevant context for terminal operations"""
        
        # Semantic search in long-term memory
        long_term_results = await self.vector_store.similarity_search(
            query=query,
            filters={'session_id': session_id},
            k=max_results // 2
        )
        
        # Recent working memory
        working_memory = await self.redis.hgetall(f"working_memory:{session_id}")
        recent_memories = []
        
        for memory_id, memory_data in working_memory.items():
            data = json.loads(memory_data)
            if self._is_relevant_to_query(data, query):
                recent_memories.append(data)
                
        # Combine and rank results
        return {
            'long_term_context': long_term_results,
            'recent_context': recent_memories[-5:],  # Last 5 relevant memories
            'session_summary': await self._get_session_summary(session_id)
        }
```

## Testing Strategy

### Unit Testing

```python
# tests/unit/test_warp_memory_agent.py
import pytest
from unittest.mock import AsyncMock, Mock
from src.agents.memory_agent import WarpMemoryAgent

class TestWarpMemoryAgent:
    
    @pytest.fixture
    async def memory_agent(self):
        redis_client = AsyncMock()
        vector_store = AsyncMock()
        config = {
            'session_timeout': 3600,
            'max_context_window': 4000,
            'auto_summarize': True
        }
        return WarpMemoryAgent(redis_client, vector_store, config)
    
    @pytest.mark.asyncio
    async def test_store_memory(self, memory_agent):
        """Test memory storage functionality"""
        session_id = "test_session_123"
        memory_data = {
            'type': 'command',
            'content': 'ls -la',
            'context': {'cwd': '/home/user'}
        }
        
        result = await memory_agent.store_memory(session_id, memory_data)
        
        assert result is not None
        assert isinstance(result, str)
        memory_agent.redis_client.hset.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_retrieve_context(self, memory_agent):
        """Test context retrieval"""
        session_id = "test_session_123"
        query = "list files"
        
        # Mock Redis response
        memory_agent.redis_client.hgetall.return_value = {
            'mem_1': '{"type": "command", "content": "ls -la", "timestamp": "2024-01-01T12:00:00"}'
        }
        
        result = await memory_agent.retrieve_context(session_id, query)
        
        assert 'recent_context' in result
        assert 'long_term_context' in result
        assert 'session_summary' in result
```

### Integration Testing

```python
# tests/integration/test_warp_agents.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.cli.warp_integration import WarpIntegration

class TestWarpAgentIntegration:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    async def warp_integration(self):
        config = {
            'agents': {
                'memory_agent': {'session_timeout': 3600},
                'search_agent': {'similarity_threshold': 0.7},
                'task_agent': {'max_concurrent_tasks': 5}
            }
        }
        integration = WarpIntegration(config)
        await integration.initialize_agents()
        return integration
    
    @pytest.mark.asyncio
    async def test_terminal_command_processing(self, warp_integration):
        """Test end-to-end command processing"""
        command = "search for recent python files"
        context = {'cwd': '/home/user/projects'}
        
        result = await warp_integration.handle_terminal_command(command, context)
        
        assert 'status' in result
        assert 'results' in result
        assert result['status'] == 'success'
        
    def test_api_health_check(self, client):
        """Test API health endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
```

### Performance Testing

```python
# tests/performance/test_memory_performance.py
import pytest
import asyncio
import time
from src.services.memory_service import MemoryService

class TestMemoryPerformance:
    
    @pytest.mark.asyncio
    async def test_memory_storage_performance(self):
        """Test memory storage performance under load"""
        memory_service = MemoryService(redis_client, vector_store)
        
        # Test storing 1000 memories
        start_time = time.time()
        tasks = []
        
        for i in range(1000):
            task = memory_service.store_working_memory(
                session_id=f"perf_test_{i % 10}",
                memory_data={
                    'type': 'command',
                    'content': f'test command {i}',
                    'timestamp': time.time()
                }
            )
            tasks.append(task)
            
        await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Should complete within 5 seconds
        assert (end_time - start_time) < 5.0
        
    @pytest.mark.asyncio
    async def test_search_performance(self):
        """Test search performance with large dataset"""
        # Implementation for search performance testing
        pass
```

## Deployment Guide

### Docker Deployment

```dockerfile
# docker/warp-agents.dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Create non-root user
RUN useradd -m -u 1000 warp-agent
USER warp-agent

# Expose port
EXPOSE 8000

# Start command
CMD ["./scripts/start_warp_agents.sh"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis/redis-stack:7.2.0-v0
    ports:
      - "6379:6379"
      - "8001:8001"
    volumes:
      - redis-data:/data
    environment:
      - REDIS_ARGS=--appendonly yes
      
  warp-memory-server:
    build:
      context: .
      dockerfile: docker/warp-agents.dockerfile
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - WARP_AGENT_MODE=true
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      
  celery-worker:
    build:
      context: .
      dockerfile: docker/warp-agents.dockerfile
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    command: celery -A src.core.celery_app worker --loglevel=info
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs

volumes:
  redis-data:
```

### Production Deployment

```bash
# scripts/deploy_production.sh
#!/bin/bash

set -e

echo "Starting production deployment..."

# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Run database migrations
docker-compose -f docker-compose.prod.yml run --rm warp-memory-server \
    python -m alembic upgrade head

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
sleep 30

# Run health checks
docker-compose -f docker-compose.prod.yml run --rm warp-memory-server \
    python -m pytest tests/integration/test_health.py

echo "Production deployment completed successfully!"
```

## Monitoring and Logging

### Structured Logging

```python
# src/core/logging.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class WarpAgentFormatter(logging.Formatter):
    """Custom formatter for Warp agent logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add agent-specific fields
        if hasattr(record, 'agent_id'):
            log_data['agent_id'] = record.agent_id
        if hasattr(record, 'session_id'):
            log_data['session_id'] = record.session_id
        if hasattr(record, 'command'):
            log_data['command'] = record.command
            
        return json.dumps(log_data, default=str)

def setup_logging(config: Dict[str, Any]) -> None:
    """Configure logging for Warp agents"""
    
    # Create formatter
    formatter = WarpAgentFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler(config.get('log_file', 'warp-agents.log'))
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=config.get('log_level', 'INFO'),
        handlers=[console_handler, file_handler],
        format='%(message)s'
    )
```

### Health Monitoring

```python
# src/api/routers/health.py
from fastapi import APIRouter, Depends, HTTPException
from src.core.database import get_redis_client
from src.core.vector_stores import get_vector_store
from src.agents.memory_agent import WarpMemoryAgent

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check for Warp agents"""
    
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'components': {}
    }
    
    # Check Redis connection
    try:
        redis_client = get_redis_client()
        await redis_client.ping()
        health_status['components']['redis'] = 'healthy'
    except Exception as e:
        health_status['components']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Check vector store
    try:
        vector_store = get_vector_store()
        await vector_store.health_check()
        health_status['components']['vector_store'] = 'healthy'
    except Exception as e:
        health_status['components']['vector_store'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Check agents
    try:
        # Quick agent functionality test
        health_status['components']['agents'] = 'healthy'
    except Exception as e:
        health_status['components']['agents'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    return health_status

@router.get("/metrics")
async def get_metrics():
    """Return system metrics for monitoring"""
    
    redis_client = get_redis_client()
    
    # Redis metrics
    redis_info = await redis_client.info()
    
    # Memory usage
    memory_usage = await redis_client.info('memory')
    
    # Agent metrics
    active_sessions = await redis_client.scard('active_sessions')
    
    return {
        'redis': {
            'connected_clients': redis_info.get('connected_clients', 0),
            'used_memory': memory_usage.get('used_memory', 0),
            'keyspace_hits': redis_info.get('keyspace_hits', 0),
            'keyspace_misses': redis_info.get('keyspace_misses', 0)
        },
        'agents': {
            'active_sessions': active_sessions,
            'memory_operations_per_second': 0,  # Implement counter
            'search_operations_per_second': 0,  # Implement counter
            'task_queue_size': 0  # Implement queue size check
        }
    }
```

## Security Considerations

### Authentication & Authorization

```python
# src/core/auth.py
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

class WarpAuthManager:
    """Authentication manager for Warp agent integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.secret_key = config['secret_key']
        self.algorithm = config.get('algorithm', 'HS256')
        
    async def authenticate_warp_agent(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """Authenticate Warp agent requests"""
        
        try:
            payload = jwt.decode(
                credentials.credentials,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Validate agent permissions
            agent_id = payload.get('agent_id')
            if not agent_id:
                raise HTTPException(status_code=403, detail="Invalid agent credentials")
                
            # Check if agent is authorized for requested operations
            permissions = payload.get('permissions', [])
            
            return {
                'agent_id': agent_id,
                'permissions': permissions,
                'session_id': payload.get('session_id'),
                'expires_at': payload.get('exp')
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def generate_agent_token(
        self, 
        agent_id: str, 
        permissions: list, 
        session_id: str = None
    ) -> str:
        """Generate JWT token for Warp agent"""
        
        payload = {
            'agent_id': agent_id,
            'permissions': permissions,
            'session_id': session_id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
```

### Data Protection

```python
# src/core/encryption.py
import base64
import hashlib
from cryptography.fernet import Fernet
from typing import str, bytes

class WarpDataProtection:
    """Data protection utilities for Warp agent memory"""
    
    def __init__(self, encryption_key: str):
        # Derive key from config
        key = base64.urlsafe_b64encode(
            hashlib.sha256(encryption_key.encode()).digest()
        )
        self.cipher = Fernet(key)
    
    def encrypt_memory(self, data: str) -> str:
        """Encrypt memory data before storage"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_memory(self, encrypted_data: str) -> str:
        """Decrypt memory data after retrieval"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def hash_session_id(self, session_id: str) -> str:
        """Hash session ID for privacy"""
        return hashlib.sha256(session_id.encode()).hexdigest()[:16]
```

## Performance Optimization

### Redis Configuration

```conf
# config/redis.conf
# Memory optimizations for Warp agents
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence configuration
save 900 1
save 300 10
save 60 10000

# Network optimizations
tcp-keepalive 300
timeout 0

# RediSearch configuration
loadmodule /opt/redis-stack/lib/redisearch.so
loadmodule /opt/redis-stack/lib/rejson.so

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log
```

### Vector Store Optimization

```python
# src/core/vector_stores.py
from typing import Dict, Any, List
from abc import ABC, abstractmethod

class VectorStoreOptimizer:
    """Optimization utilities for vector stores"""
    
    @staticmethod
    def optimize_redis_vector_store(config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize Redis vector store for Warp agents"""
        
        optimized_config = config.copy()
        
        # Optimize for terminal-based queries
        optimized_config.update({
            'vector_dimension': 384,  # Smaller dimension for faster search
            'index_type': 'HNSW',    # Hierarchical Navigable Small World
            'distance_metric': 'COSINE',
            'initial_cap': 10000,
            'max_connections': 16,
            'ef_construction': 200,
            'ef_runtime': 10
        })
        
        return optimized_config
    
    @staticmethod
    def optimize_batch_operations(batch_size: int = 100) -> int:
        """Optimize batch size for memory operations"""
        import psutil
        
        # Adjust batch size based on available memory
        available_memory = psutil.virtual_memory().available
        
        if available_memory > 8 * 1024**3:  # 8GB
            return min(batch_size * 2, 500)
        elif available_memory < 2 * 1024**3:  # 2GB
            return max(batch_size // 2, 50)
        else:
            return batch_size
```

## Common Issues and Solutions

### Issue 1: Redis Connection Timeouts

**Problem**: Redis connections timing out during heavy load

**Solution**:
```python
# src/core/database.py
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

async def create_optimized_redis_pool():
    """Create optimized Redis connection pool"""
    
    pool = ConnectionPool(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        password=config.REDIS_PASSWORD,
        max_connections=50,
        retry_on_timeout=True,
        socket_timeout=30,
        socket_connect_timeout=30,
        socket_keepalive=True,
        socket_keepalive_options={}
    )
    
    return redis.Redis(connection_pool=pool)
```

### Issue 2: Memory Leaks in Long-Running Sessions

**Problem**: Working memory growing unbounded

**Solution**:
```python
# src/services/memory_service.py
async def cleanup_expired_sessions(self):
    """Clean up expired sessions and working memory"""
    
    current_time = time.time()
    session_timeout = self.config.get('session_timeout', 3600)
    
    # Find expired sessions
    active_sessions = await self.redis.smembers('active_sessions')
    
    for session_id in active_sessions:
        last_activity = await self.redis.get(f'session_activity:{session_id}')
        
        if last_activity and (current_time - float(last_activity)) > session_timeout:
            # Clean up working memory
            await self.redis.delete(f'working_memory:{session_id}')
            await self.redis.srem('active_sessions', session_id)
            await self.redis.delete(f'session_activity:{session_id}')
```

### Issue 3: Slow Vector Search Performance

**Problem**: Vector similarity search taking too long

**Solution**:
```python
# src/services/search_service.py
async def optimized_similarity_search(
    self, 
    query: str, 
    filters: Dict[str, Any] = None,
    k: int = 10
) -> List[Dict[str, Any]]:
    """Optimized similarity search with caching"""
    
    # Generate cache key
    cache_key = hashlib.md5(f"{query}:{filters}:{k}".encode()).hexdigest()
    
    # Check cache first
    cached_result = await self.redis.get(f"search_cache:{cache_key}")
    if cached_result:
        return json.loads(cached_result)
    
    # Perform search with optimizations
    results = await self.vector_store.similarity_search(
        query=query,
        filters=filters or {},
        k=k,
        fetch_k=k * 2,  # Fetch more candidates for better results
        include_metadata=True
    )
    
    # Cache results for 5 minutes
    await self.redis.setex(
        f"search_cache:{cache_key}",
        300,
        json.dumps(results, default=str)
    )
    
    return results
```

## Reference Resources

- [Redis Stack Documentation](https://redis.io/docs/stack/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Warp Terminal Agent API](https://docs.warp.dev/features/ai)
- [OAuth2 Implementation Guide](https://oauth.net/2/)
- [Vector Database Comparison](https://github.com/erikbern/ann-benchmarks)
- [Python Async Best Practices](https://docs.python.org/3/library/asyncio.html)

## Changelog

### v2.0.0 (2025-01-15) - Warp Terminal Fork
- Complete re-architecture for Warp terminal agent integration
- Added WarpMemoryAgent, WarpSearchAgent, and WarpTaskAgent
- Implemented terminal-optimized CLI interfaces
- Enhanced Redis optimization for terminal workloads
- Added comprehensive monitoring and logging
- Improved security with agent-specific authentication

### v2.1.0 (Planned - 2025-02-01)
- Advanced command completion and suggestions
- Real-time collaboration features for terminal sessions
- Enhanced vector search with hybrid retrieval
- Machine learning-based memory categorization
- Performance optimizations for large-scale deployments

### v2.2.0 (Planned - 2025-03-01)
- Multi-tenant support for team environments
- Advanced analytics and insights dashboard
- Integration with popular terminal tools (tmux, screen, etc.)
- GraphQL API for complex queries
- Kubernetes deployment manifests

---

**Note**: This agents.md file is specifically optimized for Warp terminal agent integration. For original Claude/Cursor implementations, refer to the upstream repository documentation.
