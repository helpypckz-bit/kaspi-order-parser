from __future__ import annotations

import logging

import pytest

pd = pytest.importorskip("pandas")

from excel import ExcelService


def test_read_order_codes_accepts_whitespace_header(tmp_path) -> None:
    input_file = tmp_path / "orders.xlsx"
    pd.DataFrame({" Order Code ": [1022135385, "1022135386"]}).to_excel(input_file, index=False)

    codes = ExcelService(logging.getLogger("test")).read_order_codes(input_file)

    assert codes == ["1022135385", "1022135386"]


def test_read_order_codes_accepts_headerless_one_column_file(tmp_path) -> None:
    input_file = tmp_path / "orders.xlsx"
    pd.DataFrame([1022135385, 1022135386]).to_excel(input_file, index=False, header=False)

    codes = ExcelService(logging.getLogger("test")).read_order_codes(input_file)

    assert codes == ["1022135385", "1022135386"]


def test_read_order_codes_keeps_first_numeric_value_when_excel_has_no_header(tmp_path) -> None:
    input_file = tmp_path / "orders.xlsx"
    pd.DataFrame([1023997750, 1023998917]).to_excel(input_file, index=False, header=False)

    codes = ExcelService(logging.getLogger("test")).read_order_codes(input_file)

    assert codes == ["1023997750", "1023998917"]
