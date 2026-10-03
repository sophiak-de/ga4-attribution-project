# Attribution Assumptions and Edge Cases

## Assumptions

### Conversion Definition
A GA4 `purchase` event is treated as a conversion. Each conversion is uniquely identified using `user_pseudo_id` and the purchase event timestamp.

### Identity Resolution
`user_pseudo_id` is used as the user identifier. Cross-device and authenticated-user identity stitching are outside the scope of this implementation.

### Touchpoint Definition
One GA4 session is treated as one attribution touchpoint and is identified using `user_pseudo_id` and `ga_session_id`.

Session source, medium, and campaign are derived from the earliest available non-null event-level traffic values within the session.

### Attribution Window
Only touchpoints occurring at or before the purchase timestamp are eligible. The implementation uses all observed pre-conversion history available in the sample dataset rather than a fixed-duration lookback window.

### Attribution Models
First-Click assigns the conversion to the earliest eligible session.

Last-Click assigns the conversion to the most recent eligible session. Direct sessions are included, so this is not a last-non-direct-click model.

### Tie-Breaking
Touchpoint timestamp is the primary ordering field. `ga_session_id` is used as a deterministic secondary ordering field when required.

## Edge Cases

### Direct Traffic with Missing Marketing Fields
Some valid sessions contain null event-level source, medium, and campaign values. These sessions are retained and classified as `(direct) / (none) / (not set)` rather than being discarded.

This case was discovered during reconciliation when the initial attribution output contained 5,691 conversions while the source contained 5,692 purchases. Correcting direct-session handling produced a complete 5,692-to-5,692 reconciliation for both First-Click and Last-Click.

### Post-Conversion Activity
Sessions occurring after a purchase are explicitly excluded so that future user activity cannot receive credit for an earlier conversion.

### Streaming Environment Limitation
The Python producer implements BigQuery streaming using `insert_rows_json()`. BigQuery Sandbox returned HTTP 403 because streaming inserts require billing. SQL DML inserts were also unavailable.

For the billing-free demonstration, five sample events were materialized using `CREATE OR REPLACE TABLE ... AS SELECT`. This fallback demonstrates downstream table and dashboard behavior but is not presented as successful real-time streaming.

### Duplicate / Retried Streaming Events
Each streaming event contains an `event_id`. In production, retries should preserve a deterministic event ID and downstream processing should enforce one canonical record per event ID.