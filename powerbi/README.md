# Power BI assets

Everything required to build the interactive report lives in this folder.
The report is assembled in **Power BI Desktop** using the exported star schema;
the build steps are in [`build_guide.md`](build_guide.md).

| File | Purpose |
|------|---------|
| `FactTransactions.csv` | Transaction fact table (grain = one transaction) |
| `DimDate.csv` | Calendar dimension (year → day, weekend flag) |
| `DimBank.csv` | Bank dimension (used for sent **and** received, role-playing) |
| `DimCity.csv` | City dimension |
| `DimMerchant.csv` | Merchant dimension |
| `upi_transactions.csv` | Denormalised flat table — handy for a quick single-table import |
| `dax_measures.md` | Every DAX measure, grouped and commented |
| `data_model.md` | Star-schema diagram and relationship settings |
| `build_guide.md` | Step-by-step report build, page by page |
| `UPI_Theme.json` | Custom colour/typography theme for the report |
| `screenshots/` | Drop exported report screenshots here |

## Regenerate the data

```bash
python -m src.run_analysis
```

This rewrites all five CSVs and the flat file from the latest dataset. In Power
BI Desktop, click **Refresh** to pull the new numbers.

## Why there is no `.pbix` committed

A `.pbix` is a binary VertiPaq archive — it can't be reviewed, diffed or
generated reliably as text. Exporting the model as CSV plus a documented DAX
catalogue keeps the whole pipeline reproducible in Git: the same guide rebuilds
an identical report, and refreshing is a one-liner. If you do build a `.pbix`,
save it here as `UPI_Transactions_Analysis.pbix` and add it to `.gitignore` if it
gets large.
