with source as (

    select
        event_date,
        event_timestamp,
        timestamp_micros(event_timestamp) as event_time,
        event_name,
        user_pseudo_id,

         (
            select value.int_value
            from unnest(event_params)
            where key = 'ga_session_id'
        ) as ga_session_id,

        (
            select value.string_value
            from unnest(event_params)
            where key = 'source'
        ) as event_source,

        (
            select value.string_value
            from unnest(event_params)
            where key = 'medium'
        ) as event_medium,

        (
            select value.string_value
            from unnest(event_params)
            where key = 'campaign'
        ) as event_campaign,



        traffic_source.source as user_acquisition_source,
        traffic_source.medium as user_acquisition_medium,
        traffic_source.name as user_acquisition_campaign

    from {{ source('ga4', 'events') }}

)

select *
from source
where user_pseudo_id is not null
