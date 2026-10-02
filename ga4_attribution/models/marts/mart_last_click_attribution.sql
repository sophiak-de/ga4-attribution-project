with ranked_touchpoints as (

    select
        conversion_id,
        user_pseudo_id,
        purchase_time,
        ga_session_id,
        touchpoint_time,
        source,
        medium,
        campaign,

        row_number() over (
            partition by conversion_id
            order by touchpoint_event_timestamp desc, ga_session_id desc
        ) as touch_rank

    from {{ ref('int_conversion_touchpoints') }}

)

select
    conversion_id,
    user_pseudo_id,
    purchase_time,
    ga_session_id,
    touchpoint_time,
    coalesce(source, '(direct)') as attributed_source,
    coalesce(medium, '(none)') as attributed_medium,
    coalesce(campaign, '(not set)') as attributed_campaign,
    1 as attributed_conversions

from ranked_touchpoints

where touch_rank = 1
