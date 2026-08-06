from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from models import Order


class ExcelService:
    REQUIRED_COLUMN = "OrderCode"
    SUPPORTED_COLUMN_NAMES = {
        "ordercode",
        "code",
        "order",
        "номерзаказа",
        "заказ",
    }

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def read_order_codes(self, input_file: Path) -> list[str]:
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_file}")

        frame = pd.read_excel(input_file, dtype=str)
        column = self._detect_order_code_column(frame)
        if column is None:
            frame = pd.read_excel(input_file, dtype=str, header=None)
            column = self._detect_headerless_order_code_column(frame)

        if column is None:
            available = ", ".join(str(column_name) for column_name in frame.columns)
            raise ValueError(
                f"Input Excel must contain an {self.REQUIRED_COLUMN} column. "
                f"Available columns: {available or 'none'}. "
                "Use a column named OrderCode or a one-column Excel file with order codes."
            )

        codes = self._extract_codes(frame[column])
        if not codes:
            raise ValueError("Input Excel contains no order codes")
        self.logger.info("Loaded %s order codes", len(codes))
        return codes

    def write_orders(self, output_file: Path, orders: list[Order]) -> None:
        frame = pd.DataFrame([order.to_row() for order in orders])
        if output_file.parent != Path("."):
            output_file.parent.mkdir(parents=True, exist_ok=True)
        frame.to_excel(output_file, index=False)
        self.logger.info("Saved result to %s", output_file)

    def _detect_order_code_column(self, frame: pd.DataFrame) -> Any | None:
        normalized_columns = {self._normalize_column(column): column for column in frame.columns}
        for supported_name in self.SUPPORTED_COLUMN_NAMES:
            if supported_name in normalized_columns:
                return normalized_columns[supported_name]
        if len(frame.columns) == 1:
            only_column = frame.columns[0]
            if self._looks_like_order_code(only_column):
                return None
            self.logger.warning(
                "OrderCode column was not found; using the only column '%s' as order codes",
                only_column,
            )
            return only_column
        return None

    def _detect_headerless_order_code_column(self, frame: pd.DataFrame) -> Any | None:
        if frame.empty or len(frame.columns) != 1:
            return None
        first_value = str(frame.iloc[0, 0]).strip() if not pd.isna(frame.iloc[0, 0]) else ""
        if self._normalize_column(first_value) in self.SUPPORTED_COLUMN_NAMES:
            frame.drop(index=frame.index[0], inplace=True)
        self.logger.warning(
            "Using first column as order codes because no Excel header row was detected"
        )
        return frame.columns[0]

    def _looks_like_order_code(self, value: Any) -> bool:
        text = str(value).strip().replace(" ", "")
        if text.endswith(".0"):
            text = text[:-2]
        return text.isdigit() and len(text) >= 6

    def _extract_codes(self, values: pd.Series) -> list[str]:
        codes: list[str] = []
        for value in values.dropna():
            code = str(value).strip()
            if code.endswith(".0"):
                code = code[:-2]
            if code:
                codes.append(code)
        return codes

    def _normalize_column(self, value: Any) -> str:
        return str(value).strip().lower().replace(" ", "").replace("_", "")
