import os
import importlib
from datetime import datetime, timedelta
from typing import Optional

import requests

from libs.facebook import Insights, get
from libs.bigquery import load
from models.AdsInsights.base import FBAdsInsights

DATE_FORMAT = "%Y-%m-%d"

SESSION = requests.Session()


def factory(table: str) -> FBAdsInsights:
    try:
        module = importlib.import_module(f"models.AdsInsights.{table}")
        return getattr(module, table)
    except (ImportError, AttributeError):
        raise ValueError(table)


def transform_add_batched_at(rows: Insights) -> Insights:
    return [
        {
            **row,
            "_batched_at": datetime.utcnow().isoformat(timespec="seconds"),
        }
        for row in rows
    ]


def get_time_range(
    start: Optional[str],
    end: Optional[str],
) -> tuple[datetime, datetime]:
    return (
        (datetime.utcnow() - timedelta(days=8))
        if not start
        else datetime.strptime(start, DATE_FORMAT)
    ), datetime.utcnow() if not end else datetime.strptime(end, DATE_FORMAT)


def run(
    model: FBAdsInsights,
    ads_account_id: str,
    start: Optional[str],
    end: Optional[str],
) -> dict:
    data = get(model, ads_account_id, *get_time_range(start, end))
    response = {
        "ads_account_id": ads_account_id,
        "start": start,
        "end": end,
        "num_processed": len(data),
    }
    if len(data) > 0:
        response["output_rows"] = load(
            model,
            os.getenv("DATASET", "Facebook_dev"),
            ads_account_id,
            transform_add_batched_at(model["transform"](data)),
        )
    return response
