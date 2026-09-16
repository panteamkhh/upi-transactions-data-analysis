"""Tests for :mod:`src.feature_engineering`."""

from __future__ import annotations

import pandas as pd

from src import config, feature_engineering


def test_all_feature_columns_are_added(featured_df: pd.DataFrame) -> None:
    for column in feature_engineering.feature_columns():
        assert column in featured_df.columns, column


def test_temporal_features_are_correct(featured_df: pd.DataFrame) -> None:
    row = featured_df.loc[featured_df["TransactionID"] == "TXN0003"].iloc[0]
    assert row["Year"] == 2024
    assert row["Quarter"] == 1
    assert row["Month"] == 3
    assert row["MonthName"] == "Mar"
    assert row["Hour"] == 10


def test_success_flags(featured_df: pd.DataFrame) -> None:
    failed = featured_df.loc[featured_df["TransactionID"] == "TXN0002"].iloc[0]
    assert failed["IsSuccess"] == 0
    assert failed["IsFailed"] == 1


def test_age_and_amount_buckets(featured_df: pd.DataFrame) -> None:
    aged = featured_df.loc[featured_df["TransactionID"] == "TXN0001"].iloc[0]
    assert aged["AgeGroup"] == "20-25"
    assert aged["AmountBand"] == "<250"

    high = featured_df.loc[featured_df["TransactionID"] == "TXN0004"].iloc[0]
    assert high["AmountBand"] == "1500+"


def test_revenue_only_for_successful_payments(featured_df: pd.DataFrame) -> None:
    successful_payment = featured_df.loc[featured_df["TransactionID"] == "TXN0001"].iloc[0]
    expected = round(successful_payment[config.AMOUNT_COLUMN] * config.MDR_RATE, 4)
    assert successful_payment["EstimatedRevenue"] == expected

    failed = featured_df.loc[featured_df["TransactionID"] == "TXN0002"].iloc[0]
    assert failed["EstimatedRevenue"] == 0.0

    transfer = featured_df.loc[featured_df["TransactionID"] == "TXN0005"].iloc[0]
    assert transfer["EstimatedRevenue"] == 0.0


def test_same_bank_flag(featured_df: pd.DataFrame) -> None:
    same = featured_df.loc[featured_df["TransactionID"] == "TXN0003"].iloc[0]
    assert same["IsSameBank"] == 1
    different = featured_df.loc[featured_df["TransactionID"] == "TXN0001"].iloc[0]
    assert different["IsSameBank"] == 0
