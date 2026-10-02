import streamlit as st
from google.cloud import bigquery
import pandas as pd

PROJECT_ID = "electric-folio-510313-h6"

client = bigquery.Client(project=PROJECT_ID)

st.set_page_config(
    page_title="GA4 Attribution Dashboard",
    layout="wide"
)

st.title("GA4 Attribution Dashboard")
st.caption("First-Click vs Last-Click Attribution | GA4 Public Dataset")


@st.cache_data(ttl=60)
def run_query(query):
    return client.query(query).to_dataframe()


# --------------------------------------------------
# 1. TOTAL CONVERSIONS
# --------------------------------------------------

totals_query = """
SELECT
    'First Click' AS attribution_model,
    COUNT(*) AS conversions
FROM `electric-folio-510313-h6.ga4_attribution.mart_first_click_attribution`

UNION ALL

SELECT
    'Last Click' AS attribution_model,
    COUNT(*) AS conversions
FROM `electric-folio-510313-h6.ga4_attribution.mart_last_click_attribution`
"""

totals = run_query(totals_query)

first_total = totals.loc[
    totals["attribution_model"] == "First Click", "conversions"
].iloc[0]

last_total = totals.loc[
    totals["attribution_model"] == "Last Click", "conversions"
].iloc[0]

col1, col2 = st.columns(2)

col1.metric("First-Click Conversions", f"{first_total:,}")
col2.metric("Last-Click Conversions", f"{last_total:,}")


# --------------------------------------------------
# 2. 14-DAY TIME SERIES
# --------------------------------------------------

st.subheader("14-Day Attribution Trend")

time_query = """
WITH combined AS (

    SELECT
        DATE(purchase_time) AS purchase_date,
        'First Click' AS attribution_model
    FROM `electric-folio-510313-h6.ga4_attribution.mart_first_click_attribution`

    UNION ALL

    SELECT
        DATE(purchase_time) AS purchase_date,
        'Last Click' AS attribution_model
    FROM `electric-folio-510313-h6.ga4_attribution.mart_last_click_attribution`

),

latest_date AS (
    SELECT MAX(purchase_date) AS max_date
    FROM combined
)

SELECT
    purchase_date,
    attribution_model,
    COUNT(*) AS conversions
FROM combined
CROSS JOIN latest_date
WHERE purchase_date BETWEEN
      DATE_SUB(max_date, INTERVAL 13 DAY)
      AND max_date
GROUP BY
    purchase_date,
    attribution_model
ORDER BY
    purchase_date,
    attribution_model
"""

time_data = run_query(time_query)

time_data["purchase_date"] = pd.to_datetime(
    time_data["purchase_date"]
)

time_data["conversions"] = pd.to_numeric(
    time_data["conversions"]
)

time_chart = time_data.pivot(
    index="purchase_date",
    columns="attribution_model",
    values="conversions"
)

st.line_chart(
    time_chart,
    x_label="Date",
    y_label="Conversions"
)


# --------------------------------------------------
# 3. CHANNEL BREAKDOWN
# --------------------------------------------------

st.subheader("Conversions by Channel")

channel_query = """
SELECT
    attributed_source AS source,
    COUNT(*) AS first_click_conversions,
    0 AS last_click_conversions
FROM `electric-folio-510313-h6.ga4_attribution.mart_first_click_attribution`
GROUP BY attributed_source

UNION ALL

SELECT
    attributed_source AS source,
    0 AS first_click_conversions,
    COUNT(*) AS last_click_conversions
FROM `electric-folio-510313-h6.ga4_attribution.mart_last_click_attribution`
GROUP BY attributed_source
"""

channel_data = run_query(channel_query)

channel_summary = (
    channel_data
    .groupby("source", as_index=False)[
        ["first_click_conversions", "last_click_conversions"]
    ]
    .sum()
    .sort_values(
        "last_click_conversions",
        ascending=False
    )
    .head(10)
)

channel_summary = channel_summary.set_index("source")

st.bar_chart(channel_summary)


# --------------------------------------------------
# 4. LIVE EVENT PANEL
# --------------------------------------------------

st.subheader("Live Event Panel")

st.caption(
    "Demo events from the realtime ingestion table. "
    "BigQuery Sandbox fallback is used for materialization."
)

live_query = """
SELECT
    event_timestamp,
    user_pseudo_id,
    event_name,
    source,
    medium,
    campaign
FROM `electric-folio-510313-h6.ga4_attribution.realtime_events`
ORDER BY event_timestamp DESC
LIMIT 20
"""

live_events = run_query(live_query)

st.dataframe(
    live_events,
    use_container_width=True,
    hide_index=True
)