"""End-to-end CLI: clean, enrich, analyse, export and plot.

Usage
-----
    python -m src.run_analysis
    python -m src.run_analysis --no-plots
    python -m src.run_analysis --input data/raw/upi_transactions.xlsx
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from . import (
    analysis,
    config,
    data_cleaning,
    data_loader,
    feature_engineering,
    powerbi_export,
    visualization,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full UPI transactions analysis pipeline.")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to the raw .xlsx workbook (defaults to config.RAW_DATA_FILE).",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip chart generation (faster CI runs).",
    )
    parser.add_argument(
        "--no-powerbi",
        action="store_true",
        help="Skip exporting the Power BI star schema.",
    )
    return parser.parse_args(argv)


def run_pipeline(
    input_path: Path | None = None,
    make_plots: bool = True,
    export_powerbi: bool = True,
) -> dict:
    """Execute every stage and return the run report."""
    started = time.perf_counter()
    config.ensure_directories()

    raw = data_loader.validate_schema(data_loader.load_raw_data(input_path))
    cleaned = data_cleaning.clean_transactions(raw)
    enriched = feature_engineering.add_features(cleaned)

    # Persist the analysis-ready table.
    enriched.to_csv(config.PROCESSED_DATA_FILE, index=False, encoding="utf-8-sig")

    reports = analysis.build_all_reports(enriched)
    kpis = analysis.overall_kpis(enriched)
    highlights = analysis.insight_highlights(enriched)

    if export_powerbi:
        powerbi_export.export_powerbi_tables(enriched)

    if make_plots:
        visualization.generate_all_plots(enriched, save=True)

    summary = {
        "kpis": kpis,
        "cleaning": data_cleaning.cleaning_report(raw, cleaned),
        "insights": highlights,
        "reports": {name: table.to_dict(orient="records") for name, table in reports.items()},
        "runtime_seconds": round(time.perf_counter() - started, 2),
    }

    config.SUMMARY_FILE.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


def _print_summary(summary: dict) -> None:
    kpis = summary["kpis"]
    print("=" * 62)
    print("UPI TRANSACTIONS DATA ANALYSIS")
    print("=" * 62)
    print(f"Period            : {kpis['date_start']} -> {kpis['date_end']}")
    print(f"Transactions      : {kpis['total_transactions']:,}")
    print(f"Success rate      : {kpis['success_rate_pct']}%")
    print(f"Total value       : {kpis['total_value']:,.2f}")
    print(f"Settled value     : {kpis['settled_value']:,.2f}")
    print(f"Estimated revenue : {kpis['estimated_revenue']:,.2f}")
    print(f"Average amount    : {kpis['average_amount']:,.2f}")
    print("-" * 62)
    print("INSIGHTS")
    for line in summary["insights"]:
        print(f"  • {line}")
    print("-" * 62)
    print(f"Runtime           : {summary['runtime_seconds']}s")
    print(f"Processed data    : {config.PROCESSED_DATA_FILE}")
    print(f"Summary report    : {config.SUMMARY_FILE}")
    print("=" * 62)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary = run_pipeline(
        input_path=args.input,
        make_plots=not args.no_plots,
        export_powerbi=not args.no_powerbi,
    )
    _print_summary(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
