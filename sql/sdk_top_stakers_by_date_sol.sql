-- forked from Top Stakers Current -- more than 5000 @ https://flipsidecrypto.xyz/edit/queries/2465eea6-0d61-4dc3-b697-1aaa770ed99d
with fact_stake as (
  select
    block_timestamp as f_block_timestamp,
    tx_id as f_tx_id,
    index as f_index,
    event_type as f_event_type,
    instruction
  from
    solana.core.fact_staking_lp_actions
),
base as (
  select
    *,
    signers [0] as fee_payer,
    post_tx_staked_balance / pow(10, 9) as net_stake,
    row_number() over (
      partition by stake_account
      order by
        block_id desc,
        index desc,
        tx_id
    ) as rn,
    fact_stake.instruction :parsed :info as info
  from
    solana.core.ez_staking_lp_actions
    left join fact_stake on (
      tx_id = fact_stake.f_tx_id
      and block_timestamp = fact_stake.f_block_timestamp
      and index = fact_stake.f_index
      and event_type = fact_stake.f_event_type
    )
  where
    SUCCEEDED = TRUE
    and block_timestamp is not null
    and event_type not in ('setLockup')
    and not (
      event_type = 'authorize'
      and stake_authority is null
    )
    and not (
      stake_authority is null
      and event_type = 'authorizeWithSeed'
      and fact_stake.instruction :parsed :info :authorityType = 'Withdrawer'
    )
    and block_timestamp :: date <= {{ date }}
),
base_with_staker as (
  select
    *,
    case
      when stake_authority is null
      and event_type = 'withdraw' then lag(stake_authority) ignore nulls over (
        partition by stake_account
        order by
          rn desc
      ) -- when stake_authority is null
      -- and event_type = 'withdraw' then info :withdrawAuthority
      when stake_authority is null
      and event_type = 'authorizeChecked' then info :newAuthority
      when stake_authority is null
      and event_type = 'initializeChecked' then info :staker
      else stake_authority
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