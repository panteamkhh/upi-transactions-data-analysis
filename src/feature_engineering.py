"""Derive the analytical columns used by every downstream consumer."""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config


def _add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    date = pd.to_datetime(df[config.DATE_COLUMN])
    df["Year"] = date.dt.year
    df["Quarter"] = date.dt.quarter
    df["YearQuarter"] = date.dt.to_period("Q").astype(str)
    df["Month"] = date.dt.month
    df["MonthName"] = date.dt.strftime("%b")
    df["YearMonth"] = date.dt.strftime("%Y-%m")
    df["Week"] = date.dt.isocalendar().week.astype(int)
    df["DayOfWeek"] = date.dt.dayofweek
    df["DayName"] = date.dt.strftime("%a")
    df["Day"] = date.dt.day
    df["IsWeekend"] = date.dt.dayofweek.isin([5, 6]).astype(int)
    return df


def _add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    hour = pd.to_datetime(
        df[config.TIME_COLUMN].astype(str), format="%H:%M:%S", errors="coerce"
    ).dt.hour
    df["Hour"] = hour

    bins = [-1, 5, 11, 16, 21, 23]
    labels = ["Night", "Morning", "Afternoon", "Evening", "Late Night"]
    df["DayPart"] = pd.cut(hour, bins=bins, labels=labels).astype("object")
    return df


def _add_segment_features(df: pd.DataFrame) -> pd.DataFrame:
    df["AgeGroup"] = pd.cut(
        df["CustomerAge"],
        bins=list(config.AGE_BINS),
        labels=list(config.AGE_LABELS),
    ).astype("object")

    df["AmountBand"] = pd.cut(
        df[config.AMOUNT_COLUMN],
        bins=list(config.AMOUNT_BINS),
        labels=list(config.AMOUNT_LABELS),
        include_lowest=True,
    ).astype("object")

    df["IsSuccess"] = (df[config.STATUS_COLUMN] == config.SUCCESS_STATUS).astype(int)
    df["IsFailed"] = (df[config.STATUS_COLUMN] == config.FAILED_STATUS).astype(int)

    df["IsSameBank"] = (
        df["BankNameSent"].astype(str) == df["BankNameReceived"].astype(str)
    ).astype(int)

    return df


def _add_financial_features(df: pd.DataFrame) -> pd.DataFrame:
    """Estimate platform revenue from a flat Merchant Discount Rate.

    The raw data has no fee column, so revenue is modelled as
    ``Amount * MDR_RATE`` for successful merchant payments and ``0`` otherwise.
    Successful value is the volume actually settled by the network.
    """
    amount = df[config.AMOUNT_COLUMN].astype(float)
    is_payment = df["TransactionType"].astype(str).eq("Payment")
    is_success = df["IsSuccess"].eq(1)

    rate = np.where(is_payment, config.MDR_RATE, config.TRANSFER_FEE_RATE)
    df["EstimatedRevenue"] = np.where(is_success, amount * rate, 0.0).round(4)
    df["SettledAmount"] = np.where(is_success, amount, 0.0).round(2)
    df["FailedAmount"] = np.where(is_success, 0.0, amount).round(2)
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``df`` enriched with all derived analytical columns."""
    out = df.copy()
    out = _add_temporal_features(out)
    out = _add_time_features(out)
    out = _add_segment_features(out)
    out = _add_financial_features(out)
    return out


def feature_columns() -> list[str]:
    """Names of the columns :func:`add_features` guarantees to add."""
    return [
        "Year",
        "Quarter",
        "YearQuarter",
        "Month",
        "MonthName",
        "YearMonth",
        "Week",
        "DayOfWeek",
        "DayName",
        "Day",
        "IsWeekend",
        "Hour",
        "DayPart",
        "AgeGroup",
        "AmountBand",
        "IsSuccess",
        "IsFailed",
        "IsSameBank",
        "EstimatedRevenue",
        "SettledAmount",
        "FailedAmount",
    ]
