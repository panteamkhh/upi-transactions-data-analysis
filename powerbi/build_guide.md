# Power BI build guide

This guide rebuilds the Power BI report from scratch using the CSV exports in
this folder. It takes about 15 minutes. Everything you need — clean data, DAX
measures, a colour theme and the model layout — is already here.

## 0. Prerequisites

- **Power BI Desktop** (free, [download](https://powerbi.microsoft.com/desktop/)).
- Run the pipeline once so the CSVs exist:

  ```bash
  python -m src.run_analysis
  ```

  You should now see `FactTransactions.csv`, `DimDate.csv`, `DimBank.csv`,
  `DimCity.csv` and `DimMerchant.csv` in this folder.

> **Why CSVs and not a `.pbix`?** A `.pbix` is a binary VertiPaq archive that
> can't be generated or reviewed as plain text. Exporting the star schema as CSV
> keeps the model fully reproducible in Git — anyone can rebuild the report with
> this guide, and re-running the pipeline refreshes every number.

## 1. Import the star schema

1. **Home → Get data → Text/CSV** and import, one at a time:
   - `FactTransactions.csv`
   - `DimDate.csv`
   - `DimBank.csv`
   - `DimCity.csv`
   - `DimMerchant.csv`
2. In each preview click **Transform Data** first, then:
   - Right-click the query → **Rename** it to the table name (remove ".csv").
   - Ensure the header row is promoted and data types are correct
     (`DateKey`, `*Key`, `Amount` = Whole/Decimal number; `Date` = Date).
   - **FactTransactions**: set `Hour`, `IsSuccess`, `IsFailed`, `IsSameBank`,
     `CustomerAge` to *Whole Number*.
3. **Close & Apply**.

## 2. Create the relationships

Open **Model view**. Power BI usually auto-detects the keys; verify and fix:

| From | To | Cardinality |
|------|----|-------------|
| `DimDate[DateKey]` | `FactTransactions[DateKey]` | 1 → * |
| `DimBank[BankKey]` | `FactTransactions[BankSentKey]` | 1 → * |
| `DimBank[BankKey]` | `FactTransactions[BankReceivedKey]` | 1 → * (make **inactive**) |
| `DimCity[CityKey]` | `FactTransactions[CityKey]` | 1 → * |
| `DimMerchant[MerchantKey]` | `FactTransactions[MerchantKey]` | 1 → * |

To deactivate the received-bank relationship: double-click the line → set
**Active = No**. See [`data_model.md`](data_model.md) for the role-playing
dimension pattern.

## 3. Mark the date table

Select `DimDate` → **Table tools → Mark as date table → Date**.

## 4. Add the measures

Create a new measure table (Model view → **Home → New table**):
`Measures = ROW ( "x", 1 )`, then hide the `x` column.
Paste each measure from [`dax_measures.md`](dax_measures.md) into it.
Format `Success Rate %`, `MoM Growth %`, `QoQ Growth %`, `Value YoY %` and
`Revenue Yield %` as **Percentage** with 1–2 decimals.

## 5. Apply the theme

**View → Themes → Browse for themes** → select `UPI_Theme.json`.
This sets the navy/teal/amber palette and the Segoe UI typography used below.

## 6. Build the report pages

### Page 1 — Executive Overview

| Visual | Fields |
|--------|--------|
| 5 × **Card** | `Total Transactions`, `Total Value`, `Success Rate %`, `Settled Value`, `Estimated Revenue` |
| **Clustered bar** | Axis `DimBank[BankNameSent]`, Value `Total Value` |
| **Pie / donut** | Legend `FactTransactions[TransactionType]`, Value `Total Transactions` |
| **Line & clustered column** | Axis `DimDate[YearMonth]`, Column `Total Value`, Line `Success Rate %` |
| **Slicers** (top strip) | `DimDate[Date]`, `DimCity[City]`, `DimMerchant[MerchantName]` |

### Page 2 — Trends & Seasonality

| Visual | Fields |
|--------|--------|
| **Line chart** | Axis `DimDate[YearMonth]`, Value `Total Value`, Tooltip `MoM Growth %` |
| **Column chart** | Axis `DimDate[QuarterName]`, Value `Total Value` |
| **Area chart** | Axis `FactTransactions[Hour]`, Value `Total Transactions` (sort by Hour) |
| **Matrix** | Rows `DimDate[Year]`, `DimDate[MonthName]`, Values `Total Value`, `MoM Growth %` |
| **Card** | `Value Last 30 Days` |

### Page 3 — Banks & Geography

| Visual | Fields |
|--------|--------|
| **Filled map** (or **Treemap**) | Location `DimCity[City]`, Size `Total Value` |
| **Bar chart** | Axis `DimCity[City]`, Value `Success Rate %` |
| **Matrix** | Rows `DimBank[BankNameSent]`, Values `Total Transactions`, `Total Value`, `Success Rate %`, `Received Value` |
| **Slicer** | `FactTransactions[PaymentMode]` |

### Page 4 — Merchants & Purpose

| Visual | Fields |
|--------|--------|
| **Bar chart** | Axis `DimMerchant[MerchantName]`, Value `Total Value`, Tooltip `Merchant Rank by Value` |
| **Donut** | Legend `FactTransactions[Purpose]`, Value `Total Value` |
| **Scatter** | X `Total Transactions`, Y `Average Transaction Value`, Details `DimMerchant[MerchantName]` |
| **Decomposition tree** | Analyze `Total Value`, Explain by `Purpose`, `MerchantName`, `City` |

### Page 5 — Customers & Devices

| Visual | Fields |
|--------|--------|
| **Column chart** | Axis `FactTransactions[AgeGroup]`, Value `Total Transactions` |
| **Donut** | Legend `FactTransactions[Gender]`, Value `Total Transactions` |
| **Bar chart** | Axis `FactTransactions[DeviceType]`, Value `Total Transactions` |
| **Bar chart** | Axis `FactTransactions[PaymentMethod]`, Value `Total Transactions` |
| **Histogram** | X `FactTransactions[AmountBand]`, Value `Total Transactions` |

### Page 6 — Transactions (detail + drill-through)

| Visual | Fields |
|--------|--------|
| **Table** | `TransactionID`, `DimDate[Date]`, `DimBank[BankNameSent]`, `DimMerchant[MerchantName]`, `Amount`, `EstimatedRevenue`, `TransactionType` |
| **Drill-through filter** | Add `TransactionID`, `DimMerchant[MerchantName]`, `DimCity[City]` to the drill-through well so Pages 1–5 can jump here |

## 7. Polish

- **Sync slicers** across pages: View → *Sync slicers* → check page pairs for
  `DimDate[Date]` and `DimCity[City]`.
- **Edit interactions** so slicers filter only the intended visuals.
- **Conditional formatting** on the success-rate matrix: Format → Cell elements
  → Font colour → *Field value* → `Success Rate Colour`.
- Add a **text box** title and the note:
  *“Revenue is estimated at a 0.9% MDR on successful payments.”*

## 8. Save & export

- **File → Save as** → `powerbi/UPI_Transactions_Analysis.pbix`.
- Optionally export page screenshots into `powerbi/screenshots/` and reference
  them from the main README.

## Keeping it fresh

Re-run the pipeline after the data changes, then in Power BI hit **Refresh**:

```bash
python -m src.run_analysis
```
