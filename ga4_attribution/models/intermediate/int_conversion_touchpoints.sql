with purchases as (

    select *
    from {{ ref('int_purchases') }}

),

touchpoints as (

    select *
    from {{ ref('int_touchpoints') }}

),

eligible_touchpoints as (

    select
        p.conversion_id,
        p.user_pseudo_id,
        p.purchase_time,

        t.ga_session_id,
        t.touchpoint_event_timestamp,
        t.touchpoint_time,
        t.source,
        t.medium,
        t.campaign

    from purchases p

    inner join touchpoints t
        on p.user_pseudo_id = t.user_pseudo_id
       and t.touchpoint_event_timestamp <= p.purchase_event_timestamp

)

select *
from eligible_touchpoints
