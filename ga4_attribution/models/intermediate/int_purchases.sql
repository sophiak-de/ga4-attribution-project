with purchases as (

    select
        user_pseudo_id,
        ga_session_id,
        event_timestamp as purchase_event_timestamp,
        event_time as purchase_time

    from {{ ref('stg_ga4_events') }}

    where event_name = 'purchase'

)

select
    concat(
        user_pseudo_id,
        '-',
        cast(purchase_event_timestamp as string)
    ) as conversion_id,

    user_pseudo_id,
    ga_session_id,
    purchase_event_timestamp,
    purchase_time

from purchases

