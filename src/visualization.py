"""Matplotlib/Seaborn charts, one per business question.

Each ``plot_*`` function returns a :class:`matplotlib.figure.Figure` and,
unless ``save=False``, writes a PNG into :data:`config.SCREENSHOTS_DIR`.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless-safe backend

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

from . import analysis, config  # noqa: E402

_PALETTE = "viridis"
_PRIMARY = "#2A6F97"
_ACCENT = "#F4A261"
_FAIL = "#E76F51"
_SUCCESS = "#2A9D8F"

sns.set_theme(style="whitegrid", context="talk")
plt.rcParams.update(
    {
        "figure.dpi": 120,
        "savefig.dpi": 130,
        "savefig.bbox": "tight",
        "axes.titleweight": "bold",
        "axes.titlesize": 15,
        "font.size": 11,
    }
)


def _finalize(fig: plt.Figure, filename: str, save: bool = True) -> plt.Figure:
    fig.tight_layout()
    if save:
        config.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(Path(config.SCREENSHOTS_DIR) / filename)
    return fig


def _bar(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    xlabel: str,
    ylabel: str,
    filename: str,
    save: bool,
    palette: str = _PALETTE,
    horizontal: bool = False,
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(11, 6))
    if horizontal:
        sns.barplot(data=data, y=x, x=y, hue=x, palette=palette, legend=False, ax=ax)
        ax.set_xlabel(ylabel)
        ax.set_ylabel(xlabel)
    else:
        sns.barplot(data=data, x=x, y=y, hue=x, palette=palette, legend=False, ax=ax)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=30)
    ax.set_title(title)
    return _finalize(fig, filename, save)


def plot_top_banks(df: pd.DataFrame, save: bool = True, top: int = 10) -> plt.Figure:
    data = analysis.transactions_by_bank(df).head(top)
    return _bar(
        data,
        "bank",
        "total_value",
        "Transaction value by sending bank",
        "Bank",
        "Total value",
        "01_value_by_bank.png",
        save,
        horizontal=True,
    )


def plot_city_distribution(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.transactions_by_city(df)
    return _bar(
        data,
        "city",
        "total_value",
        "Transaction value by city",
        "City",
        "Total value",
        "02_value_by_city.png",
        save,
    )


def plot_monthly_trend(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.monthly_trend(df)
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(
        data["YearMonth"],
        data["total_value"],
        marker="o",
        linewidth=2.4,
        color=_PRIMARY,
        label="Total value",
    )
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Total value", color=_PRIMARY)
    ax1.tick_params(axis="x", rotation=45)
    ax2 = ax1.twinx()
    ax2.plot(
        data["YearMonth"],
        data["success_rate"],
        marker="s",
        linewidth=2,
        linestyle="--",
        color=_ACCENT,
        label="Success rate %",
    )
    ax2.set_ylabel("Success rate (%)", color=_ACCENT)
    ax2.set_ylim(0, 100)
    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [line.get_label() for line in lines], loc="upper left")
    ax1.set_title("Monthly transaction value and success rate")
    return _finalize(fig, "03_monthly_trend.png", save)


def plot_quarterly_trend(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.quarterly_trend(df)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=data, x="YearQuarter", y="total_value", color=_PRIMARY, ax=ax)
    ax.set_title("Quarterly transaction value")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Total value")
    return _finalize(fig, "04_quarterly_trend.png", save)


def plot_status_breakdown(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.status_breakdown(df)
    colors = [
        _SUCCESS if status == config.SUCCESS_STATUS else _FAIL
        for status in data[config.STATUS_COLUMN]
    ]
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        data["transactions"],
        labels=data[config.STATUS_COLUMN],
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        wedgeprops={"edgecolor": "white"},
    )
    ax.set_title("Transaction status split")
    return _finalize(fig, "05_status_breakdown.png", save)


def plot_device_breakdown(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.transactions_by_device(df)
    return _bar(
        data,
        "device",
        "transactions",
        "Transactions by device",
        "Device",
        "Transactions",
        "06_device_breakdown.png",
        save,
    )


def plot_payment_method(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.transactions_by_payment_method(df)
    return _bar(
        data,
        "payment_method",
        "transactions",
        "Transactions by payment method",
        "Payment method",
        "Transactions",
        "07_payment_method.png",
        save,
    )


def plot_merchant_performance(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.transactions_by_merchant(df)
    return _bar(
        data,
        "merchant",
        "total_value",
        "Transaction value by merchant",
        "Merchant",
        "Total value",
        "08_merchant_performance.png",
        save,
        horizontal=True,
    )


def plot_purpose_breakdown(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.transactions_by_purpose(df)
    return _bar(
        data,
        "purpose",
        "total_value",
        "Transaction value by purpose",
        "Purpose",
        "Total value",
        "09_purpose_breakdown.png",
        save,
        horizontal=True,
    )


def plot_age_groups(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.transactions_by_age_group(df)
    return _bar(
        data,
        "AgeGroup",
        "transactions",
        "Transactions by customer age group",
        "Age group",
        "Transactions",
        "10_age_groups.png",
        save,
    )


def plot_peak_hours(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.peak_hours(df)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=data, x="Hour", y="transactions", marker="o", ax=ax)
    ax.fill_between(data["Hour"], data["transactions"], alpha=0.15)
    ax.set_xticks(range(0, 24))
    ax.set_title("Transaction volume by hour of day")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Transactions")
    return _finalize(fig, "11_peak_hours.png", save)


def plot_amount_distribution(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.histplot(df[config.AMOUNT_COLUMN], bins=40, kde=True, color=_PRIMARY, ax=ax)
    ax.axvline(
        df[config.AMOUNT_COLUMN].median(),
        color=_FAIL,
        linestyle="--",
        label=f"Median = {df[config.AMOUNT_COLUMN].median():.0f}",
    )
    ax.legend()
    ax.set_title("Transaction amount distribution")
    ax.set_xlabel("Amount")
    ax.set_ylabel("Frequency")
    return _finalize(fig, "12_amount_distribution.png", save)


def plot_day_of_week(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.day_of_week_activity(df)
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(data=data, x="day_name", y="total_value", color=_PRIMARY, ax=ax)
    ax.set_title("Transaction value by day of week")
    ax.set_xlabel("Day")
    ax.set_ylabel("Total value")
    return _finalize(fig, "13_day_of_week.png", save)


def plot_success_rate_by_bank(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.success_rate_by_dimension(df, "BankNameSent")
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(data=data, x="BankNameSent", y="success_rate", color=_SUCCESS, ax=ax)
    ax.set_ylim(0, 100)
    ax.set_title("Success rate by sending bank")
    ax.set_xlabel("Bank")
    ax.set_ylabel("Success rate (%)")
    return _finalize(fig, "14_success_rate_by_bank.png", save)


def plot_amount_bands(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.amount_band_distribution(df)
    return _bar(
        data,
        "AmountBand",
        "transactions",
        "Transactions by amount band",
        "Amount band",
        "Transactions",
        "15_amount_bands.png",
        save,
    )


def plot_correlation_heatmap(df: pd.DataFrame, save: bool = True) -> plt.Figure:
    data = analysis.correlation_matrix(df)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        data,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title("Correlation between numeric drivers")
    return _finalize(fig, "16_correlation_heatmap.png", save)


ALL_PLOTS = (
    plot_top_banks,
    plot_city_distribution,
    plot_monthly_trend,
    plot_quarterly_trend,
    plot_status_breakdown,
    plot_device_breakdown,
    plot_payment_method,
    plot_merchant_performance,
    plot_purpose_breakdown,
    plot_age_groups,
    plot_peak_hours,
    plot_amount_distribution,
    plot_day_of_week,
    plot_success_rate_by_bank,
    plot_amount_bands,
    plot_correlation_heatmap,
)


def generate_all_plots(df: pd.DataFrame, save: bool = True) -> list[plt.Figure]:
    """Render every chart in :data:`ALL_PLOTS`, closing each after saving."""
    figures: list[plt.Figure] = []
    for plot_function in ALL_PLOTS:
        figure = plot_function(df, save=save)
        figures.append(figure)
        if save:
            plt.close(figure)
    return figures
