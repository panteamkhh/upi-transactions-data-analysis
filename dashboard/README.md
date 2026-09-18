# Streamlit dashboard

Interactive, filterable view of the UPI transactions dataset.

## Run

From the **project root**:

```bash
streamlit run dashboard/app.py
```

Streamlit opens `http://localhost:8501` in your browser.

## How it works

- On first load the app reads `data/processed/upi_transactions_clean.csv` if it
  exists, otherwise it falls back to the raw workbook and runs the cleaning +
  feature pipeline on the fly.
- Results are cached with `st.cache_data`, so filters re-render instantly.
- Every chart is built with Plotly and follows the same navy/teal/amber palette
  as the Power BI theme (`powerbi/UPI_Theme.json`).

## Tabs

| Tab | Contents |
|-----|----------|
| Overview | KPI cards, value by bank/city, status split, month-over-month table |
| Trends | Monthly value vs. success-rate combo, quarterly bars, hourly area, day-of-week |
| Banks & Cities | City treemap, success rate by city, sent/received bank tables |
| Merchants & Purpose | Merchant and purpose rankings, detail table |
| Customers & Devices | Age, gender, device, payment-method splits, amount histogram |
| Data Explorer | All filtered rows with a one-click CSV download |

## Filters

The sidebar filters the entire app by date range, city, sending bank, merchant,
device, payment method, status and transaction type. Clearing a filter removes
that dimension from the analysis.

## Tip

Regenerate the underlying data first so the dashboard reflects the latest run:

```bash
python -m src.run_analysis
```
