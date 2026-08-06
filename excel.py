from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from models import Order


class ExcelService:
    REQUIRED_COLUMN = "OrderCode"

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def read_order_codes(self, input_file: Path) -> list[str]:
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_file}")
        frame = pd.read_excel(input_file, dtype={self.REQUIRED_COLUMN: str})
        if self.REQUIRED_COLUMN not in frame.columns:
            raise ValueError(f"Input Excel must contain {self.REQUIRED_COLUMN} column")
        codes = [str(value).strip() for value in frame[self.REQUIRED_COLUMN].dropna()]
        codes = [code for code in codes if code]
        if not codes:
            raise ValueError("Input Excel contains no order codes")
        self.logger.info("Loaded %s order codes", len(codes))
        return codes

    def write_orders(self, output_file: Path, orders: list[Order]) -> None:
        frame = pd.DataFrame([order.to_row() for order in orders])
        output_file.parent.mkdir(parents=True, exist_ok=True) if output_file.parent != Path(".") else None
        frame.to_excel(output_file, index=False)
        self.logger.info("Saved result to %s", output_file)
