"""UPI Transactions Data Analysis package.

A small, testable toolkit that loads, cleans, enriches and analyses a UPI
transactions dataset, then feeds both a Python dashboard (Streamlit) and a
Power BI report model.
"""

from __future__ import annotations

__all__ = [
    "config",
    "data_loader",
    "data_cleaning",
    "feature_engineering",
    "analysis",
    "visualization",
]

__version__ = "1.0.0"
