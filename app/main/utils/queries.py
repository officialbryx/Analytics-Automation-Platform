QUERY = """
    SELECT * FROM `google_bigquery_dataset.table1`
"""


"""
WITH sp500_ciks AS (
  -- Information Technology & Tech Giants
  SELECT 320193 AS cik, 'AAPL' AS ticker UNION ALL   -- Apple
  SELECT 789019 AS cik, 'MSFT' AS ticker UNION ALL   -- Microsoft
  SELECT 1652044 AS cik, 'GOOGL' AS ticker UNION ALL -- Alphabet (Class A)
  SELECT 1652044 AS cik, 'GOOG' AS ticker UNION ALL  -- Alphabet (Class C)
  SELECT 1018724 AS cik, 'AMZN' AS ticker UNION ALL  -- Amazon
  SELECT 1326801 AS cik, 'META' AS ticker UNION ALL  -- Meta Platforms
  SELECT 1045810 AS cik, 'NVDA' AS ticker UNION ALL  -- NVIDIA
  SELECT 1318605 AS cik, 'TSLA' AS ticker UNION ALL  -- Tesla
  SELECT 1118037 AS cik, 'AVGO' AS ticker UNION ALL  -- Broadcom
  SELECT 886035 AS cik, 'CSCO' AS ticker UNION ALL   -- Cisco Systems
  SELECT 1021808 AS cik, 'ACN' AS ticker UNION ALL    -- Accenture
  SELECT 796343 AS cik, 'ADBE' AS ticker UNION ALL   -- Adobe
  SELECT 2488 AS cik, 'AMD' AS ticker UNION ALL      -- AMD
  SELECT 50863 AS cik, 'INTC' AS ticker UNION ALL    -- Intel
  SELECT 1341439 AS cik, 'ORCL' AS ticker UNION ALL  -- Oracle
  SELECT 874761 AS cik, 'CRM' AS ticker UNION ALL   -- Salesforce
  SELECT 225282 AS cik, 'QCOM' AS ticker UNION ALL   -- Qualcomm
  SELECT 4127 AS cik, 'IBM' AS ticker UNION ALL      -- IBM

  -- Financials & Banking
  SELECT 1067983 AS cik, 'BRK.B' AS ticker UNION ALL -- Berkshire Hathaway
  SELECT 19617 AS cik, 'JPM' AS ticker UNION ALL     -- JPMorgan Chase
  SELECT 70858 AS cik, 'BAC' AS ticker UNION ALL     -- Bank of America
  SELECT 829224 AS cik, 'V' AS ticker UNION ALL      -- Visa
  SELECT 1141391 AS cik, 'MA' AS ticker UNION ALL    -- Mastercard
  SELECT 831001 AS cik, 'C' AS ticker UNION ALL      -- Citigroup
  SELECT 723254 AS cik, 'WFC' AS ticker UNION ALL    -- Wells Fargo
  SELECT 886982 AS cik, 'GS' AS ticker UNION ALL     -- Goldman Sachs
  SELECT 895421 AS cik, 'MS' AS ticker UNION ALL     -- Morgan Stanley
  SELECT 818479 AS cik, 'SCHW' AS ticker UNION ALL   -- Charles Schwab

  -- Healthcare & Pharmaceuticals
  SELECT 200406 AS cik, 'JNJ' AS ticker UNION ALL    -- Johnson & Johnson
  SELECT 310158 AS cik, 'MRK' AS ticker UNION ALL    -- Merck
  SELECT 78003 AS cik, 'PFE' AS ticker UNION ALL     -- Pfizer
  SELECT 59478 AS cik, 'LLY' AS ticker UNION ALL     -- Eli Lilly
  SELECT 1551152 AS cik, 'ABBV' AS ticker UNION ALL  -- AbbVie
  SELECT 1800 AS cik, 'ABT' AS ticker UNION ALL      -- Abbott Laboratories
  SELECT 731766 AS cik, 'UNH' AS ticker UNION ALL    -- UnitedHealth Group
  SELECT 318154 AS cik, 'AMGN' AS ticker UNION ALL    -- Amgen
  SELECT 1047127 AS cik, 'CVS' AS ticker UNION ALL   -- CVS Health

  -- Consumer Discretionary & Retail
  SELECT 104169 AS cik, 'WMT' AS ticker UNION ALL    -- Walmart
  SELECT 909832 AS cik, 'COST' AS ticker UNION ALL   -- Costco
  SELECT 27419 AS cik, 'TGT' AS ticker UNION ALL     -- Target
  SELECT 354950 AS cik, 'HD' AS ticker UNION ALL     -- Home Depot
  SELECT 60667 AS cik, 'LOW' AS ticker UNION ALL     -- Lowe's
  SELECT 63908 AS cik, 'MCD' AS ticker UNION ALL     -- McDonald's
  SELECT 320187 AS cik, 'NKE' AS ticker UNION ALL    -- Nike
  SELECT 1065280 AS cik, 'NFLX' AS ticker UNION ALL  -- Netflix
  SELECT 21344 AS cik, 'KO' AS ticker UNION ALL      -- Coca-Cola
  SELECT 77476 AS cik, 'PEP' AS ticker UNION ALL     -- PepsiCo
  SELECT 80424 AS cik, 'PG' AS ticker UNION ALL      -- Procter & Gamble

  -- Energy & Industrials
  SELECT 34088 AS cik, 'XOM' AS ticker UNION ALL     -- ExxonMobil
  SELECT 93410 AS cik, 'CVX' AS ticker UNION ALL     -- Chevron
  SELECT 18230 AS cik, 'CAT' AS ticker UNION ALL     -- Caterpillar
  SELECT 12927 AS cik, 'BA' AS ticker UNION ALL      -- Boeing
  SELECT 40545 AS cik, 'GE' AS ticker UNION ALL      -- General Electric
  SELECT 101872 AS cik, 'UNP' AS ticker UNION ALL    -- Union Pacific
  SELECT 66740 AS cik, 'MMM' AS ticker               -- 3M
)
"""