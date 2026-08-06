from __future__ import annotations

import logging
from pathlib import Path

from rich.logging import RichHandler


class LoggerService:
    def __init__(self, log_file: Path) -> None:
        self.log_file = log_file

    def configure(self, level: int = logging.INFO) -> logging.Logger:
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        logger = logging.getLogger("kaspi_order_parser")
        logger.setLevel(level)
        logger.handlers.clear()
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        console_handler = RichHandler(rich_tracebacks=True, show_time=False, show_path=False)
        console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.propagate = False
        return logger
