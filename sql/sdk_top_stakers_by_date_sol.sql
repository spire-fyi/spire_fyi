-- forked from Top Stakers Current -- more than 5000 with lag @ https://flipsidecrypto.xyz/edit/queries/6e799060-0e74-481a-81b3-649f32b27b1e
-- forked from Top Stakers Current -- more than 5000 @ https://flipsidecrypto.xyz/edit/queries/2465eea6-0d61-4dc3-b697-1aaa770ed99d
with fact_stake as (
    select
        block_timestamp as f_block_timestamp,
        tx_id as f_tx_id,
        index as f_index,
        event_type as f_event_type,
        instruction
    from
        solana.gov.fact_staking_lp_actions
),
base as (
    select
        *,
        signers [0] as fee_payer,
        post_tx_staked_balance / pow(10, 9) as net_stake,
        split_part(index :: float, '.', 1) :: int as idx_major,
        case
            when contains(index :: float :: string, '.') then split_part(index :: float, '.', 2) :: int
            else 0
        end as idx_minor,
        row_number() over (
            partition by stake_account
            order by
                block_id desc,
                tx_id asc,
                idx_major desc,
                idx_minor desc,
                event_type desc
        ) as rn,
        fact_stake.instruction :parsed :info as info
    from
        solana.gov.ez_staking_lp_actions
        left join fact_stake on (
            tx_id = fact_stake.f_tx_id
            and block_timestamp = fact_stake.f_block_timestamp
            and index = fact_stake.f_index
            and event_type = fact_stake.f_event_type
        )
    where
        SUCCEEDED = TRUE -- and block_timestamp is not null
        and event_type not in ('setLockup')
        and not (
            stake_authority is null
            and event_type = 'authorize'
        )
        and not (
            stake_authority is null
            and event_type = 'authorizeWithSeed'
            and fact_stake.instruction :parsed :info :authorityType = 'Withdrawer'
        )
        and (
            block_timestamp :: date <= {{ date }}
            or block_timestamp :: date is null
        )
),
base_with_staker as (
    select
        *,
        case
            when stake_authority is null
            and (
                event_type = 'withdraw'
                or event_type = 'deactivateDelinquent'
            ) then lag(stake_authority) ignore nulls over (
                partition by stake_account
                order by
                    rn desc
            )
            when stake_authority is null
            and event_type = 'authorizeWithSeed' then info :newAuthorized
            when stake_authority is null
            and event_type = 'authorizeChecked' then info :newAuthority
            when stake_authority is null
            and event_type = 'initializeChecked' then info :staker
            else stake_authority
        end as staker_raw,
        case
            when staker_raw is null then info :withdrawAuthority
            else staker_raw
        end as staker
    from
        base
),
latest_stake as (
    select
        staker,
        sum(net_stake) as total_stake
    from
        base_with_staker
    where
        rn = 1
    group by
        staker
),
labeled as (
    select
        staker,
        total_stake,
        case
            when staker = 'mpa4abUkjQoAvPzREkh5Mo75hZhPFQ2FSH6w7dWKuQ5' then 'Solana Foundation Delegation Account'
            else l.address_name
        end as address_name,
        l.label,
        l.label_subtype,
        l.label_type
    from
        latest_stake
        left join solana.core.dim_labels l on latest_stake.staker = l.address
    order by
        total_stake desc
)
select
    *
from
    labeled
where
    total_stake > 5000