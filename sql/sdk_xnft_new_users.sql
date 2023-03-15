with first_tx as (
    select
        signers [0] as wallet,
        min(block_timestamp :: date) as first_tx_date
    from
        solana.core.fact_events
    where
        program_id = 'xnft5aaToUM4UFETUQfj7NUDUBdvYHTVhNFThEYTm55'
    group by
        1
),
new_wallets AS (
    SELECT
        first_tx_date,
        count(distinct wallet) as new_wallets
    FROM
        first_tx
    WHERE
        first_tx_date :: date > {{ date }}
    GROUP BY
        1
)
select
    *
from
    new_wallets