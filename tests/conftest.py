"""Shared pytest fixtures.

The tests build a tiny, self-contained UPI table instead of reading the 2.4 MB
workbook, so the suite stays fast and deterministic. One dedicated test loads
the real dataset when it is present and skips otherwise.
"""

from __future__ import annotations

import datetime as dt

import pandas as pd
import pytest

from src import config, data_cleaning, feature_engineering


def _make_rows() -> list[dict]:
    base = {
        "BankNameSent": "SBI Bank",
        "BankNameReceived": "HDFC Bank",
        "RemainingBalance": 5000.0,
        "City": "Delhi",
        "Gender": "Male",
        "TransactionType": "Payment",
        "Status": config.SUCCESS_STATUS,
        "DeviceType": "Mobile",
        "PaymentMethod": "QR Code",
        "MerchantName": "Amazon",
        "Purpose": "Shopping",
        "CustomerAge": 30,
        "PaymentMode": "Instant",
        "Currency": "INR",
        "CustomerAccountNumber": 123456789013,
        "MerchantAccountNumber": 987654321013,
    }
    rows: list[dict] = []
    specs = [
        (
            "TXN0001",
            "2024-01-05",
            100.0,
            "SBI Bank",
            "HDFC Bank",
            "Delhi",
            "Success",
            "Mobile",
            22,
            "Payment",
        ),
        (
            "TXN0002",
            "2024-02-10",
            1500.0,
            "ICICI Bank",
            "SBI Bank",
            "Mumbai",
            "Failed",
            "Laptop",
            34,
            "Transfer",
        ),
        (
            "TXN0003",
            "2024-03-15",
            750.0,
            "Axis Bank",
            "Axis Bank",
            "Bangalore",
            "Success",
            "Tablet",
            47,
            "Payment",
        ),
        (
            "TXN0004",
            "2024-04-20",
            2500.0,
            "HDFC Bank",
            "ICICI Bank",
            "Hyderabad",
            "Success",
            "Mobile",
            58,
            "Payment",
        ),
        (
            "TXN0005",
            "2024-05-25",
            500.0,
            "SBI Bank",
            "SBI Bank",
            "Delhi",
            "Failed",
            "Mobile",
            25,
            "Transfer",
        ),
        (
            "TXN0006",
            "2024-06-30",
            999.99,
            "  ICICI Bank ",
            "HDFC Bank",
            "Mumbai",
            "Success",
            "Laptop",
            41,
            "Payment",
        ),
        (
            "TXN0007",
            "2024-07-04",
            100.0,
            "SBI Bank",
            "HDFC Bank",
            "Delhi",
            "Success",
            "Mobile",
            22,
            "Payment",
        ),
    ]
    for index, (
        txn_id,
        date,
        amount,
        sent,
        received,
        city,
        status,
        device,
        age,
        txn_type,
    ) in enumerate(specs):
        row = dict(base)
        row.update(
            {
                "TransactionID": txn_id,
                "TransactionDate": pd.Timestamp(date),
                "Amount": amount,
                "BankNameSent": sent,
                "BankNameReceived": received,
                "City": city,
                "Status": status,
                "DeviceType": device,
                "CustomerAge": age,
                "TransactionType": txn_type,
                "TransactionTime": dt.time(index + 8, 15, 30),
                "CustomerAccountNumber": 123456789013 + index,
            }
        )
        rows.append(row)
    # An exact duplicate of the first row, to prove de-duplication works.
    rows.append(dict(rows[0]))
    return rows


@pytest.fixture()
def raw_df() -> pd.DataFrame:
    return pd.DataFrame(_make_rows())


@pytest.fixture()
def cleaned_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    return data_cleaning.clean_transactions(raw_df)


@pytest.fixture()
def featured_df(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    return feature_engineering.add_features(cleaned_df)
