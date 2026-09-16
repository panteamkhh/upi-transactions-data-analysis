# Power BI DAX measures

All measures live in the **FactTransactions** table unless stated otherwise.
The model is a star schema; see [`data_model.md`](data_model.md) for the
relationships and [`build_guide.md`](build_guide.md) for import steps.

> Every measure below mirrors a calculation that already exists in `src/analysis.py`,
> so the Power BI numbers and the Python/Streamlit numbers agree by construction.

## Core volume & value

```dax
Total Transactions =
COUNTROWS ( FactTransactions )
```

```dax
Successful Transactions =
CALCULATE ( [Total Transactions], FactTransactions[IsSuccess] = 1 )
```

```dax
Failed Transactions =
[Total Transactions] - [Successful Transactions]
```

```dax
Success Rate % =
DIVIDE ( [Successful Transactions], [Total Transactions] )
```

```dax
Total Value =
SUM ( FactTransactions[Amount] )
```

```dax
Settled Value =
SUM ( FactTransactions[SettledAmount] )
```

```dax
Failed Value =
SUM ( FactTransactions[FailedAmount] )
```

```dax
Average Transaction Value =
DIVIDE ( [Total Value], [Total Transactions] )
```

## Estimated platform revenue

Revenue is *estimated* because the source data ships without a fee column.
The assumption is a **0.9 % Merchant Discount Rate on successful payments**;
transfers and failed transactions earn nothing.

```dax
Estimated Revenue =
SUM ( FactTransactions[EstimatedRevenue] )
```

```dax
Revenue per Transaction =
DIVIDE ( [Estimated Revenue], [Total Transactions] )
```

```dax
Revenue Yield % =
DIVIDE ( [Estimated Revenue], [Settled Value] )
```

## Customer & merchant reach

```dax
Unique Customers =
DISTINCTCOUNT ( FactTransactions[CustomerAccountNumber] )
```

```dax
Unique Merchants =
DISTINCTCOUNT ( DimMerchant[MerchantName] )
```

```dax
Average Transactions per Customer =
DIVIDE ( [Total Transactions], [Unique Customers] )
```

## Time intelligence

Requires the **DimDate** table marked as the model's official date table
(Table tools → *Mark as date table* → `Date`).

```dax
Value Previous Month =
CALCULATE ( [Total Value], DATEADD ( DimDate[Date], -1, MONTH ) )
```

```dax
MoM Growth % =
DIVIDE ( [Total Value] - [Value Previous Month], [Value Previous Month] )
```

```dax
Value Previous Quarter =
CALCULATE ( [Total Value], DATEADD ( DimDate[Date], -1, QUARTER ) )
```

```dax
QoQ Growth % =
DIVIDE ( [Total Value] - [Value Previous Quarter], [Value Previous Quarter] )
```

```dax
Value YoY % =
DIVIDE (
    [Total Value] - CALCULATE ( [Total Value], SAMEPERIODLASTYEAR ( DimDate[Date] ) ),
    CALCULATE ( [Total Value], SAMEPERIODLASTYEAR ( DimDate[Date] ) )
)
```

```dax
Running Total Value =
CALCULATE (
    [Total Value],
    FILTER ( ALLSELECTED ( DimDate[Date] ), DimDate[Date] <= MAX ( DimDate[Date] ) )
)
```

```dax
Value Last 30 Days =
CALCULATE (
    [Total Value],
    DATESINPERIOD ( DimDate[Date], MAX ( DimDate[Date] ), -30, DAY )
)
```

## Ranking & segmentation helpers

```dax
Merchant Rank by Value =
RANKX ( ALL ( DimMerchant[MerchantName] ), [Total Value], , DESC )
```

```dax
Top Merchant Value =
MAXX ( ALL ( DimMerchant[MerchantName] ), [Total Value] )
```

```dax
Failure Rate % =
DIVIDE ( [Failed Transactions], [Total Transactions] )
```

```dax
Avg Age =
AVERAGE ( FactTransactions[CustomerAge] )
```

```dax
Peak Hour Transactions =
MAXX (
    VALUES ( FactTransactions[Hour] ),
    CALCULATE ( [Total Transactions] )
)
```

## Conditional formatting / colour measure (optional)

```dax
Success Rate Colour =
SWITCH (
    TRUE (),
    [Success Rate %] >= 0.85, "#2A9D8F",
    [Success Rate %] >= 0.75, "#F4A261",
    "#E76F51"
)
```

## Calculated columns (not measures)

```dax
Revenue Band =
SWITCH (
    TRUE (),
    FactTransactions[EstimatedRevenue] = 0, "No revenue",
    FactTransactions[EstimatedRevenue] < 0.5, "Low",
    FactTransactions[EstimatedRevenue] < 2, "Medium",
    "High"
)
```

```dax
Hour Label =
FORMAT ( FactTransactions[Hour], "00" ) & ":00"
```
