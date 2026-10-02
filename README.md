# GA4 Real-Time Attribution Dashboard

## Overview

This project implements an end-to-end attribution pipeline using the Google Analytics 4 public ecommerce dataset in BigQuery.

The solution uses dbt to transform raw GA4 events into session-level touchpoints and purchase conversions, applies First-Click and Last-Click attribution, and visualizes the results through a Streamlit dashboard.

A Python producer is also included to demonstrate the intended real-time event ingestion flow into BigQuery.

## Technology Stack

- Google BigQuery
- dbt Core / dbt-bigquery
- Python
- Google Cloud BigQuery Python Client
- Streamlit
- Git

## Data Source

GA4 public dataset:

`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`

GCP project:

`electric-folio-510313-h6`

Output dataset:

`ga4_attribution`

## Architecture

Detailed architecture and data flow are documented in:

`architecture/architecture.md`

Historical attribution flow:

```text
GA4 Public Dataset
        |
        v
stg_ga4_events
        |
   +----+----+
   |         |
   v         v
Purchases  Session Touchpoints
   |         |
   +----+----+
        |
        v
Eligible Conversion Touchpoints
        |
   +----+----+
   |         |
   v         v
First Click  Last Click
   |         |
   +----+----+
        |
        v
Streamlit Dashboard
```

## dbt Models

### Staging

`stg_ga4_events`

Extracts required GA4 event fields including user, session, event timestamp and traffic-source parameters.

### Intermediate

`int_purchases`

Identifies purchase conversions and creates a conversion identifier.

`int_touchpoints`

Creates one marketing touchpoint per GA4 session.

`int_conversion_touchpoints`

Joins conversions to eligible touchpoints and excludes sessions occurring after the purchase.

### Marts

`mart_first_click_attribution`

Assigns each conversion to the earliest eligible touchpoint.

`mart_last_click_attribution`

Assigns each conversion to the most recent eligible touchpoint.

## Attribution Assumptions

1. A GA4 `purchase` event represents a conversion.

2. `user_pseudo_id` is used for identity resolution. Cross-device or authenticated-user identity stitching is outside the scope of this implementation.

3. A touchpoint represents one GA4 session identified by `user_pseudo_id` and `ga_session_id`.

4. Session source, medium and campaign are derived from the earliest available non-null event-level traffic parameters within the session.

5. Sessions with no event-level traffic values are retained and classified as `(direct) / (none) / (not set)`.

6. Only touchpoints occurring at or before the purchase timestamp are eligible for attribution. Post-conversion sessions cannot receive credit.

7. The current implementation uses all observed pre-conversion history available in the sample dataset rather than enforcing a fixed-duration lookback window.

8. First-Click assigns the conversion to the earliest eligible session.

9. Last-Click assigns the conversion to the most recent eligible session.

10. Touchpoint timestamp is the primary ordering field and `ga_session_id` provides deterministic secondary ordering.

11. Direct sessions are included. The Last-Click implementation is therefore not a "last non-direct click" model.

## Validation

The attribution pipeline was reconciled against the source purchase count:

| Metric | Count |
| --- | ---: |
| Source purchase events | 5,692 |
| First-Click attributed conversions | 5,692 |
| Last-Click attributed conversions | 5,692 |

During development, one conversion was initially missing from the attribution output.

Investigation showed that the corresponding direct session had null event-level source, medium and campaign values. The touchpoint logic was corrected to retain valid sessions with missing marketing fields and classify them as direct traffic.

## Streaming Demo

The intended real-time path is:

```text
Python Producer
      |
      v
BigQuery Streaming API
      |
      v
realtime_events
      |
      v
Streamlit Live Panel
```

`streaming/stream_events.py` generates sample events and uses the BigQuery Python client's `insert_rows_json()` method.

Each event contains an `event_id`, timestamp, user identifier, event name, source, medium and campaign.

### BigQuery Sandbox Limitation

During execution, the producer reached BigQuery but returned HTTP 403 because streaming inserts are unavailable in BigQuery Sandbox without billing.

SQL DML `INSERT` was also unavailable in the Sandbox environment.

Billing was intentionally not enabled for this take-home assessment.

For the billing-free demonstration, five sample events were materialized into `realtime_events` using a `CREATE OR REPLACE TABLE ... AS SELECT` query.

This fallback demonstrates downstream table materialization and dashboard consumption, but it is not presented as successful real-time streaming.

## Idempotency and Deduplication

The streaming design uses an `event_id` for every event and passes the event identifier through `row_ids`.

For a production implementation:

- retries should preserve a deterministic event identifier
- duplicate event IDs should be detected downstream
- only one canonical row should be retained per event ID
- transient failures should use exponential backoff
- persistent failures should be sent to a replay or dead-letter mechanism

## Dashboard

The Streamlit dashboard provides:

- First-Click conversion total
- Last-Click conversion total
- 14-day attribution time series
- channel-level First-Click vs Last-Click comparison
- live/recent event panel using `realtime_events`

The 14-day First-Click and Last-Click total lines can overlap because every purchase receives exactly one conversion credit under both models. Attribution differences are more visible in the channel-level breakdown.

## Runbook

### 1. Authenticate with Google Cloud

```bash
gcloud auth application-default login
```

### 2. Navigate to the dbt project

```bash
cd ga4_attribution
```

### 3. Validate dbt connectivity

```bash
dbt debug
```

### 4. Build the dbt models

```bash
dbt run
```

### 5. Run data-quality tests

```bash
dbt test
```

Expected validation:

- 5,692 source purchases
- 5,692 First-Click conversions
- 5,692 Last-Click conversions

### 6. Run the real-time producer

From the repository root:

```bash
python streaming/stream_events.py
```

A billing-enabled BigQuery environment is required for actual streaming inserts.

In BigQuery Sandbox, use the documented query-based sample-event fallback instead.

### 7. Start the dashboard

From the repository root:

```bash
streamlit run dashboard/app.py
```

The application will start a local Streamlit server and display the attribution dashboard.

## Failure Handling

### dbt Failure

- Run `dbt debug` to verify BigQuery authentication and profile configuration.
- Review the failing model and dbt logs.
- Re-run the affected model before rebuilding downstream dependencies.

### Streaming Failure

- Capture rejected rows and API errors.
- Retry transient API failures using exponential backoff.
- Preserve event IDs during retries.
- Send persistent failures to a dead-letter or replay path.

### Data Quality Failure

Monitor:

- source purchase count
- attributed conversion count
- null conversion identifiers
- duplicate conversion identifiers
- missing session identifiers
- duplicate streaming event IDs

A mismatch between purchase count and attributed conversion count should be investigated before publishing downstream reporting.

## Monitoring

A production implementation should monitor:

- pipeline execution status
- source freshness
- event ingestion failures
- duplicate event IDs
- attribution reconciliation
- BigQuery query failures
- dashboard query failures
- processing latency

Alerts should be generated when freshness, failure rate or reconciliation checks exceed agreed thresholds.

## Cost Considerations

The public GA4 event tables can require significant BigQuery scans.

For production workloads:

- filter source data by date or partition wherever possible
- use incremental dbt models rather than repeatedly rebuilding full tables
- select only required columns
- avoid unnecessary full-table scans
- monitor BigQuery bytes processed
- cache dashboard queries where appropriate

The Streamlit application currently uses a 60-second query cache to reduce repeated dashboard queries.

## Known Limitations

- BigQuery Sandbox prevented actual streaming inserts.
- The live-event dashboard demonstration therefore uses materialized sample events.
- Identity resolution is limited to `user_pseudo_id`.
- No cross-device identity stitching is implemented.
- The attribution model currently uses observed pre-conversion history rather than a fixed lookback duration.
- The dashboard is run locally rather than deployed as a hosted application.
- The project focuses on conversion counts rather than revenue attribution.

## Repository Structure

```text
ga4-attribution-project/
|
|-- ga4_attribution/
|   |-- models/
|       |-- staging/
|       |-- intermediate/
|       |-- marts/
|
|-- streaming/
|   |-- stream_events.py
|
|-- dashboard/
|   |-- app.py
|
|-- architecture/
|   |-- architecture.md
|
|-- notes/
|   |-- attribution_logic.md
|   |-- streaming_design.md
|
|-- worklog.md
|-- README.md
```

## Development Notes

Incremental implementation decisions and debugging steps are documented in `worklog.md`.

Additional attribution and streaming design notes are available under the `notes/` directory.