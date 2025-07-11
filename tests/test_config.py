import logging

from agent_memory_server.config import get_config
from agent_memory_server.logging import configure_logging


def test_get_config_missing_file_logs_warning(caplog, monkeypatch):
    configure_logging()
    monkeypatch.setenv("REDIS_MEMORY_CONFIG", "missing_file.yaml")
    with caplog.at_level(logging.WARNING):
        config = get_config()
    assert config == {}
    assert any(
        record.message == "Config file not found"
        and record.config_file == "missing_file.yaml"
        for record in caplog.records
    )
