"""Tests for :mod:`src.powerbi_export`."""

from __future__ import annotations

import pandas as pd

from src import powerbi_export


def test_star_schema_tables_present(featured_df: pd.DataFrame) -> None:
    tables = powerbi_export.build_star_schema(featured_df)
    assert {
        "FactTransactions",
        "DimDate",
        "DimBank",
        "DimCity",
        "DimMerchant",
    }.issubset(tables.keys())


def test_fact_row_count_matches(featured_df: pd.DataFrame) -> None:
    fact = powerbi_export.build_star_schema(featured_df)["FactTransactions"]
    assert len(fact) == len(featured_df)
    assert fact["TransactionID"].is_unique


def test_foreign_keys_resolve(featured_df: pd.DataFrame) -> None:
    tables = powerbi_export.build_star_schema(featured_df)
    fact = tables["FactTransactions"]
    for key, dim in (
        ("BankSentKey", "DimBank"),
        ("CityKey", "DimCity"),
        ("MerchantKey", "DimMerchant"),
    ):
        assert fact[key].notna().all()
        assert set(fact[key]).issubset(set(tables[dim].iloc[:, 0]))


def test_export_writes_files(featured_df: pd.DataFrame, tmp_path) -> None:
    paths = powerbi_export.export_powerbi_tables(featured_df, output_dir=tmp_path)
    assert (tmp_path / "FactTransactions.csv").exists()
    assert (tmp_path / "DimDate.csv").exists()
    assert "FlatTransactions" in paths
    assert paths["FlatTransactions"].exists()
