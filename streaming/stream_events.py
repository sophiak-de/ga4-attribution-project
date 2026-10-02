from google.cloud import bigquery
from datetime import datetime, timezone
import uuid
import time


PROJECT_ID = "electric-folio-510313-h6"
DATASET_ID = "ga4_attribution"
TABLE_ID = "realtime_events"

table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

client = bigquery.Client(project=PROJECT_ID)


sample_events = [
    {
        "source": "google",
        "medium": "organic",
        "campaign": "organic_search"
    },
    {
        "source": "facebook",
        "medium": "cpc",
        "campaign": "fall_sale"
    },
    {
        "source": "email",
        "medium": "email",
        "campaign": "newsletter"
    },
    {
        "source": "linkedin",
        "medium": "social",
        "campaign": "brand_awareness"
    },
    {
        "source": "(direct)",
        "medium": "(none)",
        "campaign": "(not set)"
    }
]


for i, marketing_data in enumerate(sample_events, start=1):

    event = {
        "event_id": str(uuid.uuid4()),
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
        "user_pseudo_id": f"demo_user_{i}",
        "event_name": "page_view",
        "source": marketing_data["source"],
        "medium": marketing_data["medium"],
        "campaign": marketing_data["campaign"]
    }

    errors = client.insert_rows_json(
        table_ref,
        [event],
        row_ids=[event["event_id"]]
    )

    if errors:
        print(f"Failed: {event['event_id']} -> {errors}")
    else:
        print(
            f"Streamed: {event['event_id']} | "
            f"{event['source']} / {event['medium']}"
        )

    time.sleep(2)