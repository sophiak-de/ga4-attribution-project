# Streaming Design Notes

## Intended Real-Time Flow

Python Event Producer
        |
        v
BigQuery Streaming API
        |
        v
realtime_events
        |
        v
Streamlit Live Event Panel

The Python producer creates five sample events and attempts to send them to BigQuery using `insert_rows_json()`.

Events are generated approximately two seconds apart.

## Sandbox Limitation

The producer successfully reached the BigQuery API, but BigQuery Sandbox returned HTTP 403 because streaming inserts are not available in the free tier.

SQL DML `INSERT` was also unavailable without billing.

Billing was intentionally not enabled for this take-home assessment.

A query-based `CREATE OR REPLACE TABLE ... AS SELECT` fallback was therefore used to materialize five sample events for the dashboard demonstration.

The fallback demonstrates downstream materialization and dashboard behavior, but it is not presented as true streaming.

## Idempotency and Deduplication

- Each event contains a unique `event_id`.
- The streaming request passes the event ID through `row_ids`.
- In production, retries should preserve a deterministic event ID.
- A downstream deduplication step should enforce one record per event ID.

## Latency

The intended production design provides near-real-time event availability.

The Streamlit dashboard caches query results for 60 seconds.

The Sandbox fallback does not represent or measure actual streaming latency.

## Failure Handling

Production handling would include:

- logging rejected rows and API errors
- retrying transient failures with exponential backoff
- sending persistent failures to a dead-letter or replay mechanism
- monitoring event freshness
- monitoring duplicate event IDs
- monitoring ingestion failures
- monitoring dashboard query failures