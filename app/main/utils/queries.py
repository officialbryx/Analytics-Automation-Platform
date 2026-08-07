# 0 - start_year 
# 1 - end_year
# 2 - selected_tickers
# 3 - statement_type
# 4 - period_type
# 5 - display_unit_divider

QUERY = """


WITH user_inputs AS (
  SELECT
    {{ARRAY{2} AS selected_tickers}},
    {3} AS statement_type,
    {4} AS period_type,
    {0} AS start_year,
    {1} AS end_year,
    {5} AS display_unit_divider
)

SELECT
  sub.ticker,
  sub.company_name AS company_name,
  sub.fy AS fiscal_year,
  sub.fp AS fiscal_period,
  sub.form AS form_type,
  num.tag AS line_item_tag,
  num.ddate AS period_end_date,
  num.units AS unit_of_measure,
  -- Raw value adjusted by user selected display unit ($1, $1K, $1M)
  ROUND(num.value / inputs.display_unit_divider, 2) AS reported_value,
  CASE inputs.display_unit_divider
    WHEN 1 THEN 'Exact Dollars ($)'
    WHEN 1000 THEN 'Thousands ($K)'
    WHEN 1000000 THEN 'Millions ($M)'
  END AS display_unit_label
FROM
  `bigquery-public-data.sec_quarterly_financials.submission` AS sub
JOIN
  `bigquery-public-data.sec_quarterly_financials.numbers` AS num
  ON sub.adsh = num.adsh
CROSS JOIN
  user_inputs AS inputs
WHERE
  -- Filter by requested Tickers
  sub.ticker IN UNNEST(inputs.selected_tickers)

  -- Filter by Fiscal Year Range
  AND sub.fy BETWEEN inputs.start_year AND inputs.end_year

  -- Filter Period Type (FY = 10-K Annual Reports, Q = 10-Q Quarterly Reports)
  AND (
    (inputs.period_type = 'FY' AND sub.form = '10-K')
    OR (inputs.period_type = 'Q' AND sub.form = '10-Q')
  )

  -- Map Statement Type to SEC standard tags/forms
  AND (
    CASE inputs.statement_type
      WHEN 'IS' THEN num.tag IN (
        'Revenues', 'SalesRevenueNet', 'CostOfGoodsAndServicesSold', 
        'GrossProfit', 'OperatingExpenses', 'OperatingIncomeLoss', 
        'NetIncomeLoss', 'EarningsPerShareBasic', 'EarningsPerShareDiluted'
      )
      WHEN 'BS' THEN num.tag IN (
        'Assets', 'AssetsCurrent', 'Liabilities', 'LiabilitiesCurrent', 
        'StockholdersEquity', 'RetainedEarnings', 'CashAndCashEquivalentsAtCarryingValue'
      )
      WHEN 'CF' THEN num.tag IN (
        'NetCashProvidedByUsedInOperatingActivities', 
        'NetCashProvidedByUsedInInvestingActivities', 
        'NetCashProvidedByUsedInFinancingActivities'
      )
      ELSE TRUE
    END
  )
ORDER BY
  sub.ticker,
  sub.fy DESC,
  sub.fp,
  num.tag;
"""