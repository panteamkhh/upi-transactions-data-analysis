"""Tests for :mod:`src.data_cleaning`."""

from __future__ import annotations

import pandas as pd

from src import config, data_cleaning


def test_cleaning_drops_duplicate_rows(raw_df: pd.DataFrame) -> None:
    cleaned = data_cleaning.clean_transactions(raw_df)
    assert len(cleaned) == len(raw_df) - 1


def test_cleaning_strips_whitespace(raw_df: pd.DataFrame) -> None:
    cleaned = data_cleaning.clean_transactions(raw_df)
    assert "ICICI Bank" in set(cleaned["BankNameSent"])
    assert not cleaned["BankNameSent"].str.contains(r"^\s|\s$", regex=True).any()


def test_cleaning_parses_date_and_time_types(raw_df: pd.DataFrame) -> None:
    cleaned = data_cleaning.clean_transactions(raw_df)
    assert pd.api.types.is_datetime64_any_dtype(cleaned[config.DATE_COLUMN])
    assert cleaned[config.TIME_COLUMN].str.match(r"^\d{2}:\d{2}:\d{2}$").all()


def test_cleaning_coerces_amount_to_numeric(raw_df: pd.DataFrame) -> None:
    cleaned = data_cleaning.clean_transactions(raw_df)
    assert pd.api.types.is_numeric_dtype(cleaned[config.AMOUNT_COLUMN])


def test_cleaning_does_not_mutate_input(raw_df: pd.DataFrame) -> None:
    original = raw_df.copy(deep=True)
    data_cleaning.clean_transactions(raw_df)
    pd.testing.assert_frame_equal(raw_df, original)


def test_cleaning_report_counts(raw_df: pd.DataFrame) -> None:
    cleaned = data_cleaning.clean_transactions(raw_df)
    report = data_cleaning.cleaning_report(raw_df, cleaned)
    assert report["rows_before"] == len(raw_df)
    assert report["rows_after"] == len(cleaned)
    assert report["rows_removed"] == 1
    assert report["numeric_amounts"] is True
