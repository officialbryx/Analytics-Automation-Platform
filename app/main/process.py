import logging
from io import BytesIO
import pandas as pd
from django.urls import reverse
from main.models import Requests
from google.cloud import bigquery
from main.utils.queries import LINE_ITEMS, PER_SHARE_ITEMS, QUERY
from main.utils.tickers import TICKER_TO_CIK

from main.initialization.google import get_bigquery_client

logger = logging.getLogger(__name__)


_bq_client = None

def get_bq_client():
    global _bq_client
    if _bq_client is None:
        _bq_client = get_bigquery_client()
    return _bq_client


def build_report_bytes(report_name, results):
    df = pd.DataFrame(results) if results else pd.DataFrame({"Message": ["No data found for the selected filters"]})
    sheet_name = (str(report_name)[:31] or "Report").translate({ord(c): "_" for c in "[]:*?/\\"})
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        sheet = writer.sheets[sheet_name]
        sheet.freeze_panes = "A2"
        for column in sheet.columns:
            width = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column)
            sheet.column_dimensions[column[0].column_letter].width = min(max(width + 2, 10), 40)
    buffer.seek(0)
    return buffer


def _format_period_end(yyyymmdd):
    text = str(int(yyyymmdd))
    return f"{text[:4]}-{text[4:6]}-{text[6:]}"


def query_bigquery(tickers, statement_type, period_type, start_year, end_year):
    """Return one row per company per fiscal period, one column per line item."""
    ticker_by_cik = {TICKER_TO_CIK[t]: t for t in tickers if t in TICKER_TO_CIK}
    line_items = LINE_ITEMS[statement_type]

    if statement_type == "BS":
        num_quarters = [0]
    elif period_type == "FY":
        num_quarters = [4]
    elif statement_type == "IS":
        num_quarters = [1]
    else:
        num_quarters = [1, 2, 3]  # cash flow is reported year-to-date in 10-Qs

    config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ArrayQueryParameter("ciks", "INT64", list(ticker_by_cik)),
        bigquery.ArrayQueryParameter("tags", "STRING", [tag for _, tags in line_items for tag in tags]),
        bigquery.ArrayQueryParameter(
            "forms", "STRING", ["10-K", "10-K/A"] if period_type == "FY" else ["10-Q", "10-Q/A"]
        ),
        bigquery.ScalarQueryParameter("start_year", "INT64", int(start_year)),
        bigquery.ScalarQueryParameter("end_year", "INT64", int(end_year)),
        bigquery.ArrayQueryParameter("num_quarters", "INT64", num_quarters),
    ])
    rows = get_bq_client().query(QUERY, job_config=config).result()

    # One entry per company period; the latest filing wins
    periods = {}
    for row in rows:
        if period_type == "Q" and statement_type == "CF" and row["num_quarters"] != int(row["fiscal_period"][1:]):
            continue
        key = (row["cik"], row["fiscal_year"], row["fiscal_period"])
        entry = periods.setdefault(key, {"filed": row["date_filed"], "row": row, "facts": {}})
        if row["date_filed"] > entry["filed"]:
            entry.update(filed=row["date_filed"], row=row, facts={})
        if row["date_filed"] == entry["filed"]:
            entry["facts"][row["tag"]] = row["value"]

    results = []
    for (cik, fiscal_year, fiscal_period), entry in sorted(
        periods.items(), key=lambda item: (ticker_by_cik[item[0][0]], -item[0][1], item[0][2])
    ):
        record = {
            "Ticker": ticker_by_cik[cik],
            "Company": entry["row"]["company_name"],
            "Fiscal Year": fiscal_year,
            "Period": fiscal_period,
            "Period End Date": _format_period_end(entry["row"]["period_end"]),
        }
        for label, tags in line_items:
            value = next((entry["facts"][t] for t in tags if t in entry["facts"]), None)
            header = f"{label} ($/share)" if label in PER_SHARE_ITEMS else f"{label} ($)"
            record[header] = None if value is None else round(float(value), 2)
        results.append(record)

    logger.info(f"Built {len(results)} report rows from BigQuery")
    return results


def process(
    task_id,
    report_name,
    tickers,
    statement_type,
    period_type,
    start_year,
    end_year
):
    current_request = Requests.objects.get(task_id=task_id)

    logger.info(f"Loading data report for {report_name}")
    current_request.save()

    results = query_bigquery(
        tickers=tickers,
        statement_type=statement_type,
        period_type=period_type,
        start_year=start_year,
        end_year=end_year
    )
    logger.info(f"Successfully loaded {len(results)} rows.")

    current_request.result_data = results
    current_request.save(update_fields=["result_data"])

    return {"sheet_url": reverse("main:download_report", args=[task_id])}
