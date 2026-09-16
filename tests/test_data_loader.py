"""Tests for :mod:`src.data_loader`."""

from __future__ import annotations

import pandas as pd
import pytest

from src import config, data_loader


def test_load_raw_data_reads_expected_sheet() -> None:
    if not config.RAW_DATA_FILE.exists():
        pytest.skip("Raw workbook not available.")
    df = data_loader.load_raw_data()
    assert not df.empty
    assert set(config.REQUIRED_COLUMNS).issubset(df.columns)
    assert len(df) == 20000


def test_validate_schema_accepts_complete_frame(raw_df: pd.DataFrame) -> None:
    assert data_loader.validate_schema(raw_df) is raw_df


def test_validate_schema_rejects_missing_columns(raw_df: pd.DataFrame) -> None:
    broken = raw_df.drop(columns=["City"])
    with pytest.raises(data_loader.DataValidationError, match="City"):
        data_loader.validate_schema(broken)


def test_validate_schema_rejects_empty_frame(raw_df: pd.DataFrame) -> None:
    with pytest.raises(data_loader.DataValidationError, match="no rows"):
        data_loader.validate_schema(raw_df.iloc[0:0])


def test_load_raw_data_missing_file_raises(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        data_loader.load_raw_data(tmp_path / "nope.xlsx")
