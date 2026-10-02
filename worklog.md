# Worklog

1. Selected the GA4 obfuscated ecommerce public dataset and explored event types, purchase volume, traffic parameters and user journeys.

2. Set up BigQuery Sandbox, dbt-bigquery and Google Cloud authentication, then verified the dbt connection to BigQuery.

3. Built `stg_ga4_events` to extract the required GA4 event, session and traffic-source fields and added basic dbt tests and documentation.

4. Modeled purchase conversions and session-level marketing touchpoints using `int_purchases` and `int_touchpoints`.

5. Built `int_conversion_touchpoints` to restrict attribution to touchpoints occurring at or before each purchase.

6. Implemented First-Click and Last-Click attribution marts using deterministic `ROW_NUMBER()` ordering.

7. Reconciled attribution output against 5,692 source purchases. Investigated a one-row mismatch and traced it to a direct session with null event-level traffic fields, then corrected the session logic.

8. Implemented a Python BigQuery streaming producer. BigQuery Sandbox blocked streaming inserts, so the limitation was documented and a query-materialized five-event fallback was used for the dashboard demo.

9. Built and validated a Streamlit dashboard containing First/Last conversion totals, a 14-day attribution trend, channel breakdown and live-event panel.