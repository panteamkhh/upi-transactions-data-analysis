"""Interactive Streamlit dashboard for the UPI Transactions dataset.

Run from the project root with::

    streamlit run dashboard/app.py

The app reads the processed dataset if it exists, otherwise falls back to the
raw workbook, and applies the same cleaning + feature pipeline so the numbers
always match ``python -m src.run_analysis``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import analysis, config, data_cleaning, data_loader, feature_engineering  # noqa: E402

st.set_page_config(
    page_title="UPI Transactions Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#2A6F97"
ACCENT = "#F4A261"
SUCCESS = "#2A9D8F"
FAIL = "#E76F51"
PLOTLY_TEMPLATE = "plotly_white"


@st.cache_data(show_spinner="Loading and preparing transactions...")
def get_data() -> pd.DataFrame:
    """Load, clean and enrich the dataset (cached across reruns)."""
    try:
        df = data_loader.load_data(prefer_processed=True)
        if "IsSuccess" not in df.columns:
            df = feature_engineering.add_features(data_cleaning.clean_transactions(df))
    except FileNotFoundError:
        df = feature_engineering.add_features(
            data_cleaning.clean_transactions(data_loader.load_raw_data())
        )
    return df


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filters and return the filtered slice."""
    st.sidebar.header("Filters")

    date_min = df[config.DATE_COLUMN].min().date()
    date_max = df[config.DATE_COLUMN].max().date()
    date_range = st.sidebar.date_input(
        "Date range", value=(date_min, date_max), min_value=date_min, max_value=date_max
    )

    def multiselect(label: str, column: str) -> list[str]:
        options = sorted(df[column].dropna().astype(str).unique())
        return st.sidebar.multiselect(label, options, default=options)

    cities = multiselect("City", "City")
    banks = multiselect("Bank (sender)", "BankNameSent")
    merchants = multiselect("Merchant", "MerchantName")
    devices = multiselect("Device", "DeviceType")
    methods = multiselect("Payment method", "PaymentMethod")
    statuses = multiselect("Status", config.STATUS_COLUMN)
    txn_types = multiselect("Transaction type", "TransactionType")

    mask = pd.Series(True, index=df.index)
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        mask &= df[config.DATE_COLUMN].between(start, end)
    mask &= df["City"].astype(str).isin(cities)
    mask &= df["BankNameSent"].astype(str).isin(banks)
    mask &= df["MerchantName"].astype(str).isin(merchants)
    mask &= df["DeviceType"].astype(str).isin(devices)
    mask &= df["PaymentMethod"].astype(str).isin(methods)
    mask &= df[config.STATUS_COLUMN].astype(str).isin(statuses)
    mask &= df["TransactionType"].astype(str).isin(txn_types)

    return df[mask]


def kpi_row(kpis: dict) -> None:
    columns = st.columns(5)
    columns[0].metric("Transactions", f"{kpis['total_transactions']:,}")
    columns[1].metric("Total value", f"{kpis['total_value']:,.0f}")
    columns[2].metric("Success rate", f"{kpis['success_rate_pct']}%")
    columns[3].metric("Settled value", f"{kpis['settled_value']:,.0f}")
    columns[4].metric("Est. revenue", f"{kpis['estimated_revenue']:,.0f}")


def bar(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    orientation: str = "v",
) -> go.Figure:
    figure = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        orientation=orientation,
        template=PLOTLY_TEMPLATE,
        title=title,
        color_continuous_scale="viridis",
    )
    figure.update_layout(margin=dict(l=10, r=10, t=60, b=10), title_x=0.02)
    return figure


def overview_tab(df: pd.DataFrame) -> None:
    left, right = st.columns(2)

    with left:
        data = analysis.transactions_by_bank(df)
        st.plotly_chart(
            bar(data, "total_value", "bank", "Value by sending bank", orientation="h"),
            use_container_width=True,
        )
        data = analysis.status_breakdown(df)
        figure = px.pie(
            data,
            names=config.STATUS_COLUMN,
            values="transactions",
            hole=0.45,
            template=PLOTLY_TEMPLATE,
            title="Status split",
            color=config.STATUS_COLUMN,
            color_discrete_map={
                config.SUCCESS_STATUS: SUCCESS,
                config.FAILED_STATUS: FAIL,
            },
        )
        st.plotly_chart(figure, use_container_width=True)

    with right:
        data = analysis.transactions_by_city(df)
        st.plotly_chart(
            bar(data, "city", "total_value", "Value by city"),
            use_container_width=True,
        )
        data = analysis.transactions_by_type(df)
        st.plotly_chart(
            bar(data, "transaction_type", "transactions", "Transactions by type"),
            use_container_width=True,
        )

    st.subheader("Month-over-month growth")
    trend = analysis.monthly_trend(df)
    st.dataframe(trend, use_container_width=True, hide_index=True)


def trends_tab(df: pd.DataFrame) -> None:
    trend = analysis.monthly_trend(df)
    figure = go.Figure()
    figure.add_trace(
        go.Bar(
            x=trend["YearMonth"],
            y=trend["total_value"],
            name="Total value",
            marker_color=PRIMARY,
        )
    )
    figure.add_trace(
        go.Scatter(
            x=trend["YearMonth"],
            y=trend["success_rate"],
            name="Success rate %",
            yaxis="y2",
            line=dict(color=ACCENT, width=3),
        )
    )
    figure.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Monthly value and success rate",
        yaxis=dict(title="Total value"),
        yaxis2=dict(title="Success rate %", overlaying="y", side="right", range=[0, 100]),
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=10, r=10, t=70, b=10),
    )
    st.plotly_chart(figure, use_container_width=True)

    left, right = st.columns(2)
    with left:
        quarterly = analysis.quarterly_trend(df)
        st.plotly_chart(
            bar(quarterly, "YearQuarter", "total_value", "Quarterly value"),
            use_container_width=True,
        )
    with right:
        hours = analysis.peak_hours(df)
        st.plotly_chart(
            px.area(
                hours,
                x="Hour",
                y="transactions",
                template=PLOTLY_TEMPLATE,
                title="Volume by hour of day",
            ),
            use_container_width=True,
        )

    dow = analysis.day_of_week_activity(df)
    st.plotly_chart(
        bar(dow, "day_name", "total_value", "Value by day of week"),
        use_container_width=True,
    )


def geography_tab(df: pd.DataFrame) -> None:
    left, right = st.columns(2)
    with left:
        data = analysis.transactions_by_city(df)
        st.plotly_chart(
            px.treemap(
                data,
                path=["city"],
                values="total_value",
                template=PLOTLY_TEMPLATE,
                title="City share of value",
            ),
            use_container_width=True,
        )
    with right:
        data = analysis.success_rate_by_dimension(df, "City")
        st.plotly_chart(
            bar(data, "city", "success_rate", "Success rate by city"),
            use_container_width=True,
        )

    if {"Latitude", "Longitude"}.issubset(df.columns):
        st.map(df, use_container_width=True)
    else:
        st.info(
            "Add Latitude/Longitude columns to the dataset to enable a map view. "
            "The Live map visual is available in powerbi/UPI_Dashboard."
        )

    st.subheader("By bank (sent vs received)")
    left, right = st.columns(2)
    left.dataframe(
        analysis.transactions_by_bank(df, "sent"), use_container_width=True, hide_index=True
    )
    right.dataframe(
        analysis.transactions_by_bank(df, "received"),
        use_container_width=True,
        hide_index=True,
    )


def merchants_tab(df: pd.DataFrame) -> None:
    left, right = st.columns(2)
    with left:
        data = analysis.transactions_by_merchant(df)
        st.plotly_chart(
            bar(data, "total_value", "merchant", "Value by merchant", orientation="h"),
            use_container_width=True,
        )
    with right:
        data = analysis.transactions_by_purpose(df)
        st.plotly_chart(
            bar(data, "total_value", "purpose", "Value by purpose", orientation="h"),
            use_container_width=True,
        )

    st.subheader("Merchant detail")
    st.dataframe(
        analysis.transactions_by_merchant(df),
        use_container_width=True,
        hide_index=True,
    )


def customers_tab(df: pd.DataFrame) -> None:
    left, right = st.columns(2)
    with left:
        data = analysis.transactions_by_age_group(df)
        st.plotly_chart(
            bar(data, "AgeGroup", "transactions", "Transactions by age group"),
            use_container_width=True,
        )
    with right:
        data = analysis.transactions_by_gender(df)
        st.plotly_chart(
            px.pie(
                data,
                names="gender",
                values="transactions",
                hole=0.45,
                template=PLOTLY_TEMPLATE,
                title="Transactions by gender",
            ),
            use_container_width=True,
        )

    left, right = st.columns(2)
    with left:
        data = analysis.transactions_by_device(df)
        st.plotly_chart(
            bar(data, "device", "transactions", "Transactions by device"),
            use_container_width=True,
        )
    with right:
        data = analysis.transactions_by_payment_method(df)
        st.plotly_chart(
            bar(data, "payment_method", "transactions", "Transactions by payment method"),
            use_container_width=True,
        )

    st.subheader("Amount distribution")
    st.plotly_chart(
        px.histogram(
            df,
            x=config.AMOUNT_COLUMN,
            nbins=50,
            template=PLOTLY_TEMPLATE,
            title="Transaction amount distribution",
        ),
        use_container_width=True,
    )


def explorer_tab(df: pd.DataFrame) -> None:
    st.subheader("Filtered transactions")
    st.caption(f"{len(df):,} rows match the current filters.")
    st.dataframe(df, use_container_width=True, height=520)
    st.download_button(
        "Download filtered CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="upi_transactions_filtered.csv",
        mime="text/csv",
    )


def main() -> None:
    st.title("💳 UPI Transactions Dashboard")
    st.caption(
        "End-to-end analysis of 20,000 UPI transactions — "
        "Python pipeline, Streamlit dashboard and Power BI report."
    )

    df = get_data()
    filtered = apply_filters(df)

    if filtered.empty:
        st.warning("No transactions match the selected filters.")
        return

    kpi_row(analysis.overall_kpis(filtered))

    tabs = st.tabs(
        [
            "Overview",
            "Trends",
            "Banks & Cities",
            "Merchants & Purpose",
            "Customers & Devices",
            "Data Explorer",
        ]
    )
    with tabs[0]:
        overview_tab(filtered)
    with tabs[1]:
        trends_tab(filtered)
    with tabs[2]:
        geography_tab(filtered)
    with tabs[3]:
        merchants_tab(filtered)
    with tabs[4]:
        customers_tab(filtered)
    with tabs[5]:
        explorer_tab(filtered)

    st.sidebar.divider()
    st.sidebar.caption(
        f"Dataset: {analysis.overall_kpis(df)['date_start']} to "
        f"{analysis.overall_kpis(df)['date_end']}"
    )


if __name__ == "__main__":
    main()
