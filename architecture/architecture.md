# GA4 Real-Time Attribution Architecture

## Historical Attribution Pipeline

GA4 Public Dataset (BigQuery)
        |
        v
stg_ga4_events
        |
        +-------------------+
        |                   |
        v                   v
int_purchases        int_touchpoints
        |                   |
        +---------+---------+
                  |
                  v
      int_conversion_touchpoints
                  |
          +-------+-------+
          |               |
          v               v
mart_first_click     mart_last_click
          |               |
          +-------+-------+
                  |
                  v
          Streamlit Dashboard


## Real-Time Demo Flow

Python Event Producer
        |
        | BigQuery insert_rows_json
        v
BigQuery realtime_events
        |
        v
Streamlit Live Event Panel


## Technology Choices

- **BigQuery** - GA4 public dataset and analytical warehouse
- **dbt** - SQL transformations, model dependencies, tests and documentation
- **Python** - sample real-time event producer
- **Streamlit** - attribution dashboard
- **Git** - source control and incremental development history


## Dataset

Source:

`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`

Project:

`electric-folio-510313-h6`

Output dataset:

`ga4_attribution`


## Streaming Environment Note

The real-time producer uses the BigQuery Python client's
`insert_rows_json()` method.

During testing, BigQuery Sandbox returned HTTP 403 because streaming
inserts require billing. To keep the assessment reproducible without
enabling billing, five sample events were materialized using a
query-based fallback and displayed through the same `realtime_events`
table in the Streamlit dashboard.