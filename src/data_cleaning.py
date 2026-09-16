"""Cleaning routines that turn the raw workbook into a tidy fact table."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from . import config

# Canonical spellings for values that occasionally show up in a few variants.
_BANK_ALIASES: dict[str, str] = {
    "sbi": "SBI Bank",
    "state bank of india": "SBI Bank",
    "sbi bank": "SBI Bank",
    "icici": "ICICI Bank",
    "icici bank": "ICICI Bank",
    "axis": "Axis Bank",
    "axis bank": "Axis Bank",
    "hdfc": "HDFC Bank",
    "hdfc bank": "HDFC Bank",
}

_CRITICAL_COLUMNS: tuple[str, ...] = (
    config.ID_COLUMN,
    config.DATE_COLUMN,
    config.AMOUNT_COLUMN,
    config.STATUS_COLUMN,
)

_ID_COLUMNS: tuple[str, ...] = (
    "CustomerAccountNumber",
    "MerchantAccountNumber",
)


def _strip_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Trim surrounding whitespace from every text column."""
    for column in df.columns:
        if pd.api.types.is_string_dtype(df[column]) and not pd.api.types.is_numeric_dtype(
            df[column]
        ):
            df[column] = df[column].astype("object").str.strip()
    return df


def _canonicalise_banks(df: pd.DataFrame) -> pd.DataFrame:
    """Map known bank-name variants onto a canonical spelling."""
    for column in ("BankNameSent", "BankNameReceived"):
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("object")
                .str.strip()
                .map(lambda value: _BANK_ALIASES.get(str(value).lower(), value))
            )
    return df


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and type-cast the raw UPI transaction table.

    The function is intentionally pure: it returns a new DataFrame and never
    mutates the caller's object. Steps:

    1. Trim whitespace and canonicalise bank names.
    2. Parse the transaction date and normalise the time to ``HH:MM:SS``.
    3. Coerce numeric columns and drop rows with unusable critical fields.
    4. Keep account numbers as strings (they are identifiers, not numbers).
    5. Drop exact duplicate rows.
    """
    out = df.copy()

    out = _strip_strings(out)
    out = _canonicalise_banks(out)

    # --- dates & times -----------------------------------------------------
    if config.DATE_COLUMN in out.columns:
        out[config.DATE_COLUMN] = pd.to_datetime(out[config.DATE_COLUMN], errors="coerce")

    if config.TIME_COLUMN in out.columns:
        parsed = pd.to_datetime(
            out[config.TIME_COLUMN].astype("object").astype(str),
            format="%H:%M:%S",
            errors="coerce",
        )
        out[config.TIME_COLUMN] = parsed.dt.strftime("%H:%M:%S")

    # --- numerics ----------------------------------------------------------
    for column in (config.AMOUNT_COLUMN, "RemainingBalance", "CustomerAge"):
        if column in out.columns:
            out[column] = pd.to_numeric(out[column], errors="coerce")

    # --- identifiers as text ----------------------------------------------
    for column in _ID_COLUMNS:
        if column in out.columns:
            out[column] = out[column].astype("object").astype(str)

    # --- drop unusable rows ------------------------------------------------
    subset = [c for c in _CRITICAL_COLUMNS if c in out.columns]
    out = out.dropna(subset=subset)

    if config.AMOUNT_COLUMN in out.columns:
        out = out[out[config.AMOUNT_COLUMN] >= 0]

    out = out.drop_duplicates().reset_index(drop=True)

    # Dates should be stored without a time component.
    if config.DATE_COLUMN in out.columns:
        out[config.DATE_COLUMN] = out[config.DATE_COLUMN].dt.normalize()

    return out


def cleaning_report(before: pd.DataFrame, after: pd.DataFrame) -> dict[str, Any]:
    """Summarise what cleaning changed, for logging and the run report."""
    return {
        "rows_before": int(len(before)),
        "rows_after": int(len(after)),
        "rows_removed": int(len(before) - len(after)),
        "duplicates_removed": int(len(before) - len(before.drop_duplicates())),
        "missing_values_after": int(after.isna().sum().sum()),
        "numeric_amounts": bool(
            config.AMOUNT_COLUMN in after.columns
            and pd.api.types.is_numeric_dtype(after[config.AMOUNT_COLUMN])
        ),
        "amount_is_finite": bool(
            config.AMOUNT_COLUMN in after.columns and np.isfinite(after[config.AMOUNT_COLUMN]).all()
        ),
    }
