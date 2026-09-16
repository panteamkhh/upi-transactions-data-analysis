"""End-to-end test for the CLI pipeline in :mod:`src.run_analysis`."""

from __future__ import annotations

import pandas as pd

from src import config, run_analysis


def test_pipeline_runs_end_to_end(raw_df: pd.DataFrame, tmp_path, monkeypatch) -> None:
    raw_path = tmp_path / "raw.xlsx"
    raw_df.to_excel(raw_path, index=False)

    processed = tmp_path / "processed.csv"
    summary = tmp_path / "summary.json"
    monkeypatch.setattr(config, "PROCESSED_DATA_FILE", processed)
    monkeypatch.setattr(config, "SUMMARY_FILE", summary)

    report = run_analysis.run_pipeline(input_path=raw_path, make_plots=False, export_powerbi=False)

    assert processed.exists()
    assert summary.exists()
    assert report["kpis"]["total_transactions"] == len(raw_df) - 1
    assert "reports" in report
    assert "monthly_trend" in report["reports"]


def test_parse_args_defaults() -> None:
    args = run_analysis.parse_args([])
    assert args.no_plots is False
    assert args.no_powerbi is False
    assert args.input is None


def test_parse_args_flags() -> None:
    args = run_analysis.parse_args(["--no-plots", "--no-powerbi"])
    assert args.no_plots is True
    assert args.no_powerbi is True


def test_main_returns_zero(raw_df: pd.DataFrame, tmp_path, monkeypatch, capsys) -> None:
    raw_path = tmp_path / "raw.xlsx"
    raw_df.to_excel(raw_path, index=False)
    monkeypatch.setattr(config, "PROCESSED_DATA_FILE", tmp_path / "p.csv")
    monkeypatch.setattr(config, "SUMMARY_FILE", tmp_path / "s.json")

    exit_code = run_analysis.main(["--input", str(raw_path), "--no-plots", "--no-powerbi"])
    assert exit_code == 0
    assert "UPI TRANSACTIONS DATA ANALYSIS" in capsys.readouterr().out
