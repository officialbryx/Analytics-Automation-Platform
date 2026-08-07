from typing import Any, Dict, List
from google.cloud import bigquery
from initialization.bigquery import load_sources
from utils.queries import QUERY


def fetch_and_process_recent_users(start_date: str, limit: int = 50) -> List[Dict[str, Any]]:
    client = load_sources()

    # Define query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
            bigquery.ScalarQueryParameter("limit_val", "INT64", limit),
        ]
    )

    # Run query
    query_job = client.query(QUERY, job_config=job_config)
    results = query_job.result()

    # Process & transform raw rows
    processed_data = []
    for row in results:
        processed_data.append(
            {
                "id": row["user_id"],
            }
        )

    return processed_data

