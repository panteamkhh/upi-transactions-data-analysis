"""Tests for :mod:`src.analysis`."""

from __future__ import annotations

import pandas as pd
import pytest

from src import analysis


def test_overall_kpis(featured_df: pd.DataFrame) -> None:
    kpis = analysis.overall_kpis(featured_df)
    assert kpis["total_transactions"] == len(featured_df)
    assert kpis["successful_transactions"] == 5
    assert kpis["failed_transactions"] == 2
    assert kpis["success_rate_pct"] == pytest.approx(71.43, abs=0.01)
    assert kpis["total_value"] == pytest.approx(6449.99, abs=0.01)


def test_revenue_is_positive_and_bounded(featured_df: pd.DataFrame) -> None:
    kpis = analysis.overall_kpis(featured_df)
    assert 0 < kpis["estimated_revenue"] < kpis["settled_value"]


def test_transactions_by_bank_sorted(featured_df: pd.DataFrame) -> None:
    table = analysis.transactions_by_bank(featured_df)
    assert "bank" in table.columns
    assert table["total_value"].is_monotonic_decreasing
    assert set(table.columns) >= {"transactions", "success_rate", "share_pct"}


def test_by_bank_sides_differ(featured_df: pd.DataFrame) -> None:
    sent = analysis.transactions_by_bank(featured_df, "sent")
    received = analysis.transactions_by_bank(featured_df, "received")
    assert sent["transactions"].sum() == received["transactions"].sum()


def test_monthly_trend_has_one_row_per_month(featured_df: pd.DataFrame) -> None:
    trend = analysis.monthly_trend(featured_df)
    assert len(trend) == featured_df["YearMonth"].nunique()
    assert "mom_growth_pct" in trend.columns


def test_peak_hours_covers_full_day(featured_df: pd.DataFrame) -> None:
    hours = analysis.peak_hours(featured_df)
    assert len(hours) == 24
    assert list(hours["Hour"]) == list(range(24))
    assert hours["transactions"].sum() == len(featured_df)


def test_status_breakdown_shares_sum_to_100(featured_df: pd.DataFrame) -> None:
    breakdown = analysis.status_breakdown(featured_df)
    assert breakdown["share_pct"].sum() == pytest.approx(100.0, abs=0.01)


def test_success_rate_by_dimension(featured_df: pd.DataFrame) -> None:
    table = analysis.success_rate_by_dimension(featured_df, "BankNameSent")
    assert table["success_rate"].between(0, 100).all()


def test_correlation_matrix_is_square(featured_df: pd.DataFrame) -> None:
    matrix = analysis.correlation_matrix(featured_df)
    assert matrix.shape[0] == matrix.shape[1]
    assert (abs(matrix.values.diagonal() - 1) < 1e-9).all()


def test_insight_highlights(featured_df: pd.DataFrame) -> None:
    insights = analysis.insight_highlights(featured_df)
    assert isinstance(insights, list)
    assert len(insights) == 5
    assert all(isinstance(line, str) and line for line in insights)


def test_build_all_reports_keys(featured_df: pd.DataFrame) -> None:
    reports = analysis.build_all_reports(featured_df)
    expected = {
        "monthly_trend",
        "peak_hours",
        "status_breakdown",
        "correlation_matrix",
        "transactions_by_city",
    }
    assert expected.issubset(reports.keys())
    assert all(isinstance(table, pd.DataFrame) for table in reports.values())
