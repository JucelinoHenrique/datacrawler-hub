import json
import logging
import sys
from logging import Handler, LogRecord


class JsonStreamHandler(Handler):
    def emit(self, record: LogRecord) -> None:
        payload = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        sys.stdout.write(json.dumps(payload) + "\n")


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level)
    # limpa handlers default do uvicorn para evitar duplicação
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = JsonStreamHandler()
    root.addHandler(handler)

    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel("WARNING")
    logging.getLogger("httpx").setLevel("WARNING")
