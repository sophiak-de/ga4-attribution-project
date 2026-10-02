with session_events as (

    select
        user_pseudo_id,
        ga_session_id,
        event_timestamp,
        event_time,
        event_source,
        event_medium,
        event_campaign

    from {{ ref('stg_ga4_events') }}

    where ga_session_id is not null

),

session_touchpoints as (

    select
        user_pseudo_id,
        ga_session_id,

        min(event_timestamp) as touchpoint_event_timestamp,
        min(event_time) as touchpoint_time,

        coalesce(
            array_agg(
                event_source ignore nulls
                order by event_timestamp
                limit 1
            )[safe_offset(0)],
            '(direct)'
        ) as source,

        coalesce(
            array_agg(
                event_medium ignore nulls
                order by event_timestamp
                limit 1
            )[safe_offset(0)],
            '(none)'
        ) as medium,

        coalesce(
            array_agg(
                event_campaign ignore nulls
                order by event_timestamp
                limit 1
            )[safe_offset(0)],
            '(not set)'
        ) as campaign

    from session_events

    group by
        user_pseudo_id,
        ga_session_id

)

select *
from session_touchpoints

