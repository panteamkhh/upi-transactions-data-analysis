"""One pure function per business question.

Every function takes the enriched transaction table and returns a small,
presentation-ready DataFrame or dictionary. No plotting or file IO happens
here, which keeps the business logic independently testable.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from . import config


def _value_column(df: pd.DataFrame) -> str:
    return config.AMOUNT_COLUMN


def overall_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """Headline numbers for the executive summary."""
    total = len(df)
    successful = int(df["IsSuccess"].sum()) if "IsSuccess" in df else 0
    total_value = float(df[config.AMOUNT_COLUMN].sum())
    success_value = float(df["SettledAmount"].sum()) if "SettledAmount" in df else 0.0
    revenue = float(df["EstimatedRevenue"].sum()) if "EstimatedRevenue" in df else 0.0
    return {
        "total_transactions": total,
        "successful_transactions": successful,
        "failed_transactions": total - successful,
        "success_rate_pct": round(successful / total * 100, 2) if total else 0.0,
        "total_value": round(total_value, 2),
        "settled_value": round(success_value, 2),
        "estimated_revenue": round(revenue, 2),
        "average_amount": round(total_value / total, 2) if total else 0.0,
        "unique_customers": (
            int(df["CustomerAccountNumber"].nunique()) if "CustomerAccountNumber" in df else 0
        ),
        "unique_merchants": (int(df["MerchantName"].nunique()) if "MerchantName" in df else 0),
        "unique_cities": int(df["City"].nunique()) if "City" in df else 0,
        "date_start": str(df[config.DATE_COLUMN].min().date()),
        "date_end": str(df[config.DATE_COLUMN].max().date()),
    }


def _aggregate(
    df: pd.DataFrame,
    by: str,
    order_by: str = "total_value",
) -> pd.DataFrame:
    grouped = (
        df.groupby(by, dropna=False)
        .agg(
            transactions=(config.ID_COLUMN, "count"),
            total_value=(config.AMOUNT_COLUMN, "sum"),
            average_amount=(config.AMOUNT_COLUMN, "mean"),
            success_rate=("IsSuccess", "mean"),
            estimated_revenue=("EstimatedRevenue", "sum"),
        )
        .reset_index()
    )
    grouped["success_rate"] = (grouped["success_rate"] * 100).round(2)
    grouped["share_pct"] = (grouped["total_value"] / grouped["total_value"].sum() * 100).round(2)
    grouped = grouped.sort_values(order_by, ascending=False).reset_index(drop=True)
    return grouped.round({"total_value": 2, "average_amount": 2, "estimated_revenue": 2})


def transactions_by_bank(df: pd.DataFrame, side: str = "sent") -> pd.DataFrame:
    """Volume and value by the sending or receiving bank."""
    column = "BankNameSent" if side == "sent" else "BankNameReceived"
    result = _aggregate(df, column)
    return result.rename(columns={column: "bank"})


def transactions_by_city(df: pd.DataFrame) -> pd.DataFrame:
    return _aggregate(df, "City").rename(columns={"City": "city"})


def transactions_by_merchant(df: pd.DataFrame) -> pd.DataFrame:
    return _aggregate(df, "MerchantName").rename(columns={"MerchantName": "merchant"})


def transactions_by_purpose(df: pd.DataFrame) -> pd.DataFrame:
    return _aggregate(df, "Purpose").rename(columns={"Purpose": "purpose"})


def transactions_by_device(df: pd.DataFrame) -> pd.DataFrame:
    return _aggregate(df, "DeviceType").rename(columns={"DeviceType": "device"})


def transactions_by_payment_method(df: pd.DataFrame) -> pd.DataFrame:
    return _aggregate(df, "PaymentMethod").rename(columns={"PaymentMethod": "payment_method"})


def transactions_by_gender(df: pd.DataFrame) -> pd.DataFrame:
    return _aggregate(df, "Gender").rename(columns={"Gender": "gender"})


def transactions_by_age_group(df: pd.DataFrame) -> pd.DataFrame:
    result = _aggregate(df, "AgeGroup")
    return result.sort_values("AgeGroup").reset_index(drop=True)


def transactions_by_type(df: pd.DataFrame) -> pd.DataFrame:
    return _aggregate(df, "TransactionType").rename(columns={"TransactionType": "transaction_type"})


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Transaction value and volume rolled up per calendar month."""
    grouped = (
        df.groupby("YearMonth", dropna=False)
        .agg(
            transactions=(config.ID_COLUMN, "count"),
            total_value=(config.AMOUNT_COLUMN, "sum"),
            settled_value=("SettledAmount", "sum"),
            failed_value=("FailedAmount", "sum"),
            estimated_revenue=("EstimatedRevenue", "sum"),
            success_rate=("IsSuccess", "mean"),
        )
        .reset_index()
        .sort_values("YearMonth")
    )
    grouped["success_rate"] = (grouped["success_rate"] * 100).round(2)
    grouped["mom_growth_pct"] = (grouped["total_value"].pct_change() * 100).round(2)
    return grouped.round(
        {
            "total_value": 2,
            "settled_value": 2,
            "failed_value": 2,
            "estimated_revenue": 2,
        }
    )


def quarterly_trend(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby("YearQuarter", dropna=False)
        .agg(
            transactions=(config.ID_COLUMN, "count"),
            total_value=(config.AMOUNT_COLUMN, "sum"),
            estimated_revenue=("EstimatedRevenue", "sum"),
            success_rate=("IsSuccess", "mean"),
        )
        .reset_index()
        .sort_values("YearQuarter")
    )
    grouped["success_rate"] = (grouped["success_rate"] * 100).round(2)
    grouped["qoq_growth_pct"] = (grouped["total_value"].pct_change() * 100).round(2)
    return grouped.round({"total_value": 2, "estimated_revenue": 2})


def day_of_week_activity(df: pd.DataFrame) -> pd.DataFrame:
    order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    result = _aggregate(df, "DayName").rename(columns={"DayName": "day_name"})
    result["day_name"] = pd.Categorical(result["day_name"], categories=order, ordered=True)
    return result.sort_values("day_name").reset_index(drop=True)


def peak_hours(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby("Hour", dropna=False)
        .agg(
            transactions=(config.ID_COLUMN, "count"),
            total_value=(config.AMOUNT_COLUMN, "sum"),
        )
        .reindex(range(24), fill_value=0)
        .reset_index()
    )
    return grouped.round({"total_value": 2})


def status_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(config.STATUS_COLUMN, dropna=False)
        .agg(
            transactions=(config.ID_COLUMN, "count"),
            total_value=(config.AMOUNT_COLUMN, "sum"),
        )
        .reset_index()
    )
    grouped["share_pct"] = (grouped["transactions"] / grouped["transactions"].sum() * 100).round(2)
    return grouped.round({"total_value": 2})


def success_rate_by_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Success rate (and volume) for any categorical column."""
    grouped = (
        df.groupby(dimension, dropna=False)
        .agg(
            transactions=(config.ID_COLUMN, "count"),
            success_rate=("IsSuccess", "mean"),
            failed_transactions=("IsFailed", "sum"),
        )
        .reset_index()
    )
    grouped["success_rate"] = (grouped["success_rate"] * 100).round(2)
    return grouped.sort_values("success_rate", ascending=False).reset_index(drop=True)


def amount_band_distribution(df: pd.DataFrame) -> pd.DataFrame:
    result = _aggregate(df, "AmountBand", order_by="transactions")
    result = result.sort_values("AmountBand").reset_index(drop=True)
    return result


def same_bank_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Compare intra-bank vs inter-bank transfers."""
    grouped = (
        df.groupby("IsSameBank", dropna=False)
        .agg(
            transactions=(config.ID_COLUMN, "count"),
            total_value=(config.AMOUNT_COLUMN, "sum"),
            success_rate=("IsSuccess", "mean"),
        )
        .reset_index()
    )
    grouped["route"] = grouped["IsSameBank"].map({1: "Same bank", 0: "Different bank"})
    grouped["success_rate"] = (grouped["success_rate"] * 100).round(2)
    return grouped.round({"total_value": 2})


def top_merchants(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    return transactions_by_merchant(df).head(n)


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Correlation between the numeric business drivers."""
    columns = [
        config.AMOUNT_COLUMN,
        "CustomerAge",
        "IsSuccess",
        "EstimatedRevenue",
        "Hour",
    ]
    available = [c for c in columns if c in df.columns]
    return df[available].corr(numeric_only=True).round(3)


def insight_highlights(df: pd.DataFrame) -> list[str]:
    """Plain-language takeaways assembled from the aggregates above."""
    kpis = overall_kpis(df)
    banks = transactions_by_bank(df)
    cities = transactions_by_city(df)
    devices = transactions_by_device(df)
    hours = peak_hours(df)

    top_bank = banks.iloc[0]["bank"]
    top_city = cities.iloc[0]["city"]
    top_device = devices.iloc[0]["device"]
    peak_hour = int(hours.loc[hours["transactions"].idxmax(), "Hour"])
    best_weekday = day_of_week_activity(df).iloc[0]["day_name"]

    return [
        f"{kpis['total_transactions']:,} transactions worth "
        f"{kpis['total_value']:,.2f} processed between "
        f"{kpis['date_start']} and {kpis['date_end']}.",
        f"Overall success rate is {kpis['success_rate_pct']}%; "
        f"{kpis['failed_transactions']:,} transactions failed.",
        f"{top_bank} is the busiest sending bank and {top_city} the top city.",
        f"{top_device}s are the preferred device; activity peaks around "
        f"{peak_hour:02d}:00, with {best_weekday} the most active day.",
        f"Estimated platform revenue is {kpis['estimated_revenue']:,.2f} "
        f"(assumption: {config.MDR_RATE:.2%} MDR on successful payments).",
    ]


def build_all_reports(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Run every aggregate once and return them keyed by name."""
    reports: dict[str, pd.DataFrame] = {
        "transactions_by_bank_sent": transactions_by_bank(df, "sent"),
        "transactions_by_bank_received": transactions_by_bank(df, "received"),
        "transactions_by_city": transactions_by_city(df),
        "transactions_by_merchant": transactions_by_merchant(df),
        "transactions_by_purpose": transactions_by_purpose(df),
        "transactions_by_device": transactions_by_device(df),
        "transactions_by_payment_method": transactions_by_payment_method(df),
        "transactions_by_gender": transactions_by_gender(df),
        "transactions_by_age_group": transactions_by_age_group(df),
        "transactions_by_type": transactions_by_type(df),
        "monthly_trend": monthly_trend(df),
        "quarterly_trend": quarterly_trend(df),
        "day_of_week_activity": day_of_week_activity(df),
        "peak_hours": peak_hours(df),
        "status_breakdown": status_breakdown(df),
        "amount_band_distribution": amount_band_distribution(df),
        "same_bank_analysis": same_bank_analysis(df),
        "correlation_matrix": correlation_matrix(df),
    }
    return reports
