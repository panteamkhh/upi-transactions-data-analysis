"""Central configuration: filesystem paths and project-wide constants.

Every other module imports its paths and business constants from here so the
whole pipeline can be redirected by editing a single file.
"""

from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]

DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"

REPORTS_DIR: Path = PROJECT_ROOT / "reports"
SCREENSHOTS_DIR: Path = PROJECT_ROOT / "screenshots"
ASSETS_DIR: Path = PROJECT_ROOT / "assets"
POWERBI_DIR: Path = PROJECT_ROOT / "powerbi"

RAW_DATA_FILE: Path = RAW_DATA_DIR / "upi_transactions.xlsx"
RAW_SHEET_NAME: str = "Sheet1"

PROCESSED_DATA_FILE: Path = PROCESSED_DATA_DIR / "upi_transactions_clean.csv"
POWERBI_DATA_FILE: Path = POWERBI_DIR / "upi_transactions.csv"
SUMMARY_FILE: Path = REPORTS_DIR / "summary.json"

# --------------------------------------------------------------------------- #
# Reproducibility
# --------------------------------------------------------------------------- #
RANDOM_SEED: int = 42

# --------------------------------------------------------------------------- #
# Business constants
# --------------------------------------------------------------------------- #
SUCCESS_STATUS: str = "Success"
FAILED_STATUS: str = "Failed"

# The source data ships without any cost / fee column, so platform revenue is
# estimated rather than measured. We assume a Merchant Discount Rate (MDR) is
# earned only on *successful* merchant payments; failed transactions and
# person-to-person transfers earn nothing in this model.
MDR_RATE: float = 0.009  # 0.9% of successful Payment value
TRANSFER_FEE_RATE: float = 0.0  # P2P transfers are free in this model

# Age bucketing used across the notebook, dashboard and Power BI model.
AGE_BINS: tuple[int, ...] = (19, 25, 35, 45, 55, 120)
AGE_LABELS: tuple[str, ...] = ("20-25", "26-35", "36-45", "46-55", "56+")

# Amount bucketing (INR) used for distribution analysis.
AMOUNT_BINS: tuple[float, ...] = (0, 250, 500, 1000, 1500, float("inf"))
AMOUNT_LABELS: tuple[str, ...] = (
    "<250",
    "250-500",
    "500-1000",
    "1000-1500",
    "1500+",
)

# --------------------------------------------------------------------------- #
# Schema
# --------------------------------------------------------------------------- #
DATE_COLUMN: str = "TransactionDate"
TIME_COLUMN: str = "TransactionTime"
AMOUNT_COLUMN: str = "Amount"
STATUS_COLUMN: str = "Status"
ID_COLUMN: str = "TransactionID"

REQUIRED_COLUMNS: tuple[str, ...] = (
    "TransactionID",
    "TransactionDate",
    "Amount",
    "BankNameSent",
    "BankNameReceived",
    "RemainingBalance",
    "City",
    "Gender",
    "TransactionType",
    "Status",
    "TransactionTime",
    "DeviceType",
    "PaymentMethod",
    "MerchantName",
    "Purpose",
    "CustomerAge",
    "PaymentMode",
    "Currency",
    "CustomerAccountNumber",
    "MerchantAccountNumber",
)


def ensure_directories() -> None:
    """Create every output directory the pipeline writes to."""
    for directory in (
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        REPORTS_DIR,
        SCREENSHOTS_DIR,
        ASSETS_DIR,
        POWERBI_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)
