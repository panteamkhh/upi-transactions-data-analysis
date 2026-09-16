"""Export a Power BI friendly star schema from the enriched dataset.

The flat file is convenient for a quick import, but the intended model is a
star schema: one fact table of transactions surrounded by date, bank, city and
merchant dimensions. Both are written so either approach works.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import config


def _dim_date(df: pd.DataFrame) -> pd.DataFrame:
    date = pd.to_datetime(df[config.DATE_COLUMN])
    dim = pd.DataFrame({"DateKey": date.dt.strftime("%Y%m%d").astype(int)})
    dim["Date"] = date.dt.normalize()
    dim["Year"] = date.dt.year
    dim["Quarter"] = date.dt.quarter
    dim["QuarterName"] = "Q" + date.dt.quarter.astype(str)
    dim["Month"] = date.dt.month
    dim["MonthName"] = date.dt.strftime("%B")
    dim["MonthShort"] = date.dt.strftime("%b")
    dim["YearMonth"] = date.dt.strftime("%Y-%m")
    dim["Day"] = date.dt.day
    dim["DayName"] = date.dt.strftime("%A")
    dim["DayShort"] = date.dt.strftime("%a")
    dim["DayOfWeek"] = date.dt.dayofweek + 1
    dim["IsWeekend"] = date.dt.dayofweek.isin([5, 6]).astype(int)
    return dim.drop_duplicates(subset=["DateKey"]).sort_values("DateKey").reset_index(drop=True)


def _dim_from_column(df: pd.DataFrame, column: str, key_name: str) -> pd.DataFrame:
    values = sorted(df[column].dropna().astype(str).unique())
    return pd.DataFrame({key_name: range(1, len(values) + 1), column: values})


def build_star_schema(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return the fact table plus every dimension table."""
    date = pd.to_datetime(df[config.DATE_COLUMN])
    date_key = date.dt.strftime("%Y%m%d").astype(int)

    dim_date = _dim_date(df)
    dim_bank = _dim_from_column(df, "BankNameSent", "BankKey")
    bank_map = dict(zip(dim_bank["BankNameSent"], dim_bank["BankKey"], strict=True))

    dim_city = _dim_from_column(df, "City", "CityKey")
    city_map = dict(zip(dim_city["City"], dim_city["CityKey"], strict=True))

    dim_merchant = _dim_from_column(df, "MerchantName", "MerchantKey")
    merchant_map = dict(zip(dim_merchant["MerchantName"], dim_merchant["MerchantKey"], strict=True))

    fact = pd.DataFrame(
        {
            "TransactionID": df[config.ID_COLUMN],
            "DateKey": date_key,
            "BankSentKey": df["BankNameSent"].map(bank_map),
            "BankReceivedKey": df["BankNameReceived"].map(bank_map),
            "CityKey": df["City"].map(city_map),
            "MerchantKey": df["MerchantName"].map(merchant_map),
            "CustomerAccountNumber": df["CustomerAccountNumber"],
            "Amount": df[config.AMOUNT_COLUMN],
            "RemainingBalance": df["RemainingBalance"],
            "IsSuccess": df["IsSuccess"],
            "IsFailed": df["IsFailed"],
            "EstimatedRevenue": df["EstimatedRevenue"],
            "SettledAmount": df["SettledAmount"],
            "FailedAmount": df["FailedAmount"],
            "IsSameBank": df["IsSameBank"],
            "Hour": df["Hour"],
            "DayPart": df["DayPart"],
            "TransactionType": df["TransactionType"],
            "DeviceType": df["DeviceType"],
            "PaymentMethod": df["PaymentMethod"],
            "PaymentMode": df["PaymentMode"],
            "Currency": df["Currency"],
            "Purpose": df["Purpose"],
            "Gender": df["Gender"],
            "AgeGroup": df["AgeGroup"],
            "CustomerAge": df["CustomerAge"],
            "AmountBand": df["AmountBand"],
        }
    )

    return {
        "FactTransactions": fact,
        "DimDate": dim_date,
        "DimBank": dim_bank,
        "DimCity": dim_city,
        "DimMerchant": dim_merchant,
    }


def export_powerbi_tables(
    df: pd.DataFrame,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write the star schema as CSV files and return their paths."""
    output_dir = Path(output_dir) if output_dir is not None else config.POWERBI_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    tables = build_star_schema(df)
    paths: dict[str, Path] = {}
    for name, table in tables.items():
        path = output_dir / f"{name}.csv"
        table.to_csv(path, index=False, encoding="utf-8-sig")
        paths[name] = path

    flat_path = config.POWERBI_DATA_FILE
    df.to_csv(flat_path, index=False, encoding="utf-8-sig")
    paths["FlatTransactions"] = flat_path
    return paths
