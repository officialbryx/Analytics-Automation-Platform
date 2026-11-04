"""SEC query and the line items shown in each report."""

# (column label, [SEC tags to try in order])
LINE_ITEMS = {
    "IS": [
        ("Revenue", ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"]),
        ("Cost of Revenue", ["CostOfRevenue", "CostOfGoodsAndServicesSold"]),
        ("Gross Profit", ["GrossProfit"]),
        ("Operating Expenses", ["OperatingExpenses"]),
        ("Operating Income", ["OperatingIncomeLoss"]),
        ("Net Income", ["NetIncomeLoss"]),
        ("EPS Basic", ["EarningsPerShareBasic"]),
        ("EPS Diluted", ["EarningsPerShareDiluted"]),
    ],
    "BS": [
        ("Cash", ["CashAndCashEquivalentsAtCarryingValue"]),
        ("Current Assets", ["AssetsCurrent"]),
        ("Total Assets", ["Assets"]),
        ("Current Liabilities", ["LiabilitiesCurrent"]),
        ("Total Liabilities", ["Liabilities"]),
        ("Retained Earnings", ["RetainedEarningsAccumulatedDeficit"]),
        ("Shareholders Equity", ["StockholdersEquity"]),
    ],
    "CF": [
        ("Operating Cash Flow", ["NetCashProvidedByUsedInOperatingActivities"]),
        ("Investing Cash Flow", ["NetCashProvidedByUsedInInvestingActivities"]),
        ("Financing Cash Flow", ["NetCashProvidedByUsedInFinancingActivities"]),
    ],
}

PER_SHARE_ITEMS = {"EPS Basic", "EPS Diluted"}

# number_of_quarters: 0 = balance sheet, 1 = one quarter, 4 = full year
# period_end_date = period: current period only, no prior-year columns
# GROUP BY: removes duplicate rows
QUERY = """
SELECT
  sub.central_index_key AS cik,
  sub.company_name AS company_name,
  sub.fiscal_year AS fiscal_year,
  sub.fiscal_period_focus AS fiscal_period,
  sub.period AS period_end,
  sub.date_filed AS date_filed,
  num.measure_tag AS tag,
  num.number_of_quarters AS num_quarters,
  MAX(num.value) AS value
FROM `bigquery-public-data.sec_quarterly_financials.submission` AS sub
JOIN `bigquery-public-data.sec_quarterly_financials.numbers` AS num
  ON sub.submission_number = num.submission_number
WHERE sub.central_index_key IN UNNEST(@ciks)
  AND sub.fiscal_year BETWEEN @start_year AND @end_year
  AND sub.form IN UNNEST(@forms)
  AND num.measure_tag IN UNNEST(@tags)
  AND num.period_end_date = sub.period
  AND num.number_of_quarters IN UNNEST(@num_quarters)
  AND num.num_dimensions = 0
  AND num.coregistrant IS NULL
  AND num.units = 'USD'
GROUP BY cik, company_name, fiscal_year, fiscal_period, period_end, date_filed, tag, num_quarters
"""
