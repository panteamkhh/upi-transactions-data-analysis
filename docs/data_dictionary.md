# Data dictionary

Reference for every column in `data/raw/upi_transactions.xlsx` and the derived
columns added by `src/feature_engineering.py`. Types are the types *after*
cleaning (`src/data_cleaning.py`).

## Source columns

| # | Column | Type | Description | Example |
|---|--------|------|-------------|---------|
| 1 | `TransactionID` | string | Unique transaction identifier. Primary key. | `TXN00001` |
| 2 | `TransactionDate` | date | Date the transaction was initiated (normalised, no time). | `2024-02-02` |
| 3 | `Amount` | float | Transaction value in the stated `Currency`. Range 0.05–1,999.87. | `271.64` |
| 4 | `BankNameSent` | string | Customer's (sending) bank. | `SBI Bank` |
| 5 | `BankNameReceived` | string | Beneficiary / merchant bank. | `HDFC Bank` |
| 6 | `RemainingBalance` | float | Account balance after the transaction. | `5557.02` |
| 7 | `City` | string | City of the transaction. | `Delhi` |
| 8 | `Gender` | string | Customer gender. | `Female` |
| 9 | `TransactionType` | string | `Transfer` (P2P) or `Payment` (merchant). | `Transfer` |
| 10 | `Status` | string | `Success` or `Failed`. Authoritative outcome. | `Success` |
| 11 | `TransactionTime` | time | Time of day, normalised to `HH:MM:SS`. | `17:12:14` |
| 12 | `DeviceType` | string | Device used: `Mobile`, `Tablet`, `Laptop`. | `Tablet` |
| 13 | `PaymentMethod` | string | `UPI ID`, `QR Code` or `Phone Number`. | `Phone Number` |
| 14 | `MerchantName` | string | Merchant (Payments only). | `Amazon` |
| 15 | `Purpose` | string | Spend category. | `Food` |
| 16 | `CustomerAge` | int | Customer age in years (20–59). | `21` |
| 17 | `PaymentMode` | string | `Instant` or `Scheduled`. | `Scheduled` |
| 18 | `Currency` | string | Currency label: `INR`, `USD`, `EUR`, `GBP`. | `USD` |
| 19 | `CustomerAccountNumber` | string | Customer account identifier (degenerate dimension). | `123456789013` |
| 20 | `MerchantAccountNumber` | string | Merchant account identifier (degenerate dimension). | `987654321013` |

## Derived columns (`src/feature_engineering.py`)

| Column | Type | Derivation |
|--------|------|------------|
| `Year` | int | `TransactionDate.year` |
| `Quarter` | int | `TransactionDate.quarter` (1–4) |
| `YearQuarter` | string | e.g. `2024Q1` |
| `Month` | int | 1–12 |
| `MonthName` | string | Abbreviated month, e.g. `Feb` |
| `YearMonth` | string | Sortable `YYYY-MM`, e.g. `2024-02` |
| `Week` | int | ISO week number |
| `DayOfWeek` | int | 0 = Monday … 6 = Sunday |
| `DayName` | string | Abbreviated weekday, e.g. `Mon` |
| `Day` | int | Day of month |
| `IsWeekend` | int | 1 if Saturday/Sunday |
| `Hour` | int | Hour of `TransactionTime` (0–23) |
| `DayPart` | string | `Night`, `Morning`, `Afternoon`, `Evening`, `Late Night` |
| `AgeGroup` | string | Buckets from `config.AGE_BINS` → `20-25`, `26-35`, `36-45`, `46-55`, `56+` |
| `AmountBand` | string | Buckets from `config.AMOUNT_BINS` → `<250`, `250-500`, `500-1000`, `1000-1500`, `1500+` |
| `IsSuccess` | int | 1 when `Status == "Success"` |
| `IsFailed` | int | 1 when `Status == "Failed"` |
| `IsSameBank` | int | 1 when sending and receiving banks match |
| `EstimatedRevenue` | float | `Amount × 0.9%` for successful `Payment` rows, else 0 |
| `SettledAmount` | float | `Amount` when successful, else 0 |
| `FailedAmount` | float | `Amount` when failed, else 0 |

## Power BI mapping

`src/powerbi_export.py` reshapes these into a star schema:

- `FactTransactions` — one row per transaction, with surrogate foreign keys.
- `DimDate`, `DimBank`, `DimCity`, `DimMerchant` — conformed dimensions.

See [`powerbi/data_model.md`](../powerbi/data_model.md) for the relationships.
