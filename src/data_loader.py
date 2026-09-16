"""Load and validate the raw UPI transactions workbook."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from . import config


class DataValidationError(ValueError):
    """Raised when a dataset does not match the expected UPI schema."""


def load_raw_data(
    path: str | Path | None = None,
    sheet_name: str | None = None,
) -> pd.DataFrame:
    """Read the raw Excel workbook into a DataFrame.

    Parameters
    ----------
    path:
        Path to the ``.xlsx`` workbook. Defaults to
        :data:`config.RAW_DATA_FILE`.
    sheet_name:
        Worksheet to read. Defaults to :data:`config.RAW_SHEET_NAME`.
    """
    path = Path(path) if path is not None else config.RAW_DATA_FILE
    sheet_name = sheet_name or config.RAW_SHEET_NAME

    if not path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {path}. "
            "Download it into data/raw/ or update src/config.py."
        )

    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    return df


def validate_schema(
    df: pd.DataFrame,
    required: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Return ``df`` if it contains every required column, else raise."""
    required = tuple(required) if required is not None else config.REQUIRED_COLUMNS
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise DataValidationError("Dataset is missing required columns: " + ", ".join(missing))
    if df.empty:
        raise DataValidationError("Dataset contains no rows.")
    return df


def load_processed_data(path: str | Path | None = None) -> pd.DataFrame:
    """Load the cleaned, feature-enriched dataset produced by the pipeline."""
    path = Path(path) if path is not None else config.PROCESSED_DATA_FILE
    if not path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at {path}. " "Run `python -m src.run_analysis` first."
        )
    df = pd.read_csv(path, parse_dates=[config.DATE_COLUMN])
    return df


def load_data(
    prefer_processed: bool = True,
    path: str | Path | None = None,
) -> pd.DataFrame:
    """Load the processed dataset when available, otherwise the raw workbook.

    This is the convenience entry point used by the dashboard and notebook so
    they work whether or not the pipeline has been run yet.
    """
    if path is not None:
        return validate_schema(load_raw_data(path))

    if prefer_processed and config.PROCESSED_DATA_FILE.exists():
        return load_processed_data()

    return validate_schema(load_raw_data())
