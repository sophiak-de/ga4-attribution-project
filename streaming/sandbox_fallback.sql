CREATE OR REPLACE TABLE
  `electric-folio-510313-h6.ga4_attribution.realtime_events` AS

SELECT
  GENERATE_UUID() AS event_id,
  CURRENT_TIMESTAMP() AS event_timestamp,
  'demo_user_1' AS user_pseudo_id,
  'page_view' AS event_name,
  'google' AS source,
  'organic' AS medium,
  'organic_search' AS campaign

UNION ALL

SELECT
  GENERATE_UUID(),
  TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 2 SECOND),
  'demo_user_2',
  'page_view',
  'facebook',
  'cpc',
  'fall_sale'

UNION ALL

SELECT
  GENERATE_UUID(),
  TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 4 SECOND),
  'demo_user_3',
  'page_view',
  'email',
  'email',
  'newsletter'

UNION ALL

SELECT
  GENERATE_UUID(),
  TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 6 SECOND),
  'demo_user_4',
  'page_view',
  'linkedin',
  'social',
  'brand_awareness'

UNION ALL

SELECT
  GENERATE_UUID(),
  TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 8 SECOND),
  'demo_user_5',
  'page_view',
  '(direct)',
  '(none)',
  '(not set)';