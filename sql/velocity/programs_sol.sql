WITH unique_programs AS (
    SELECT
        distinct program_id as program
    from
        solana.core.fact_events
),
program_creation_date as (
    select
        program_id,
        min(block_timestamp :: date) as creation_date
    from
        solana.core.fact_events
    where
        program_id in (
            select
                program
            from
                unique_programs
        )
    group by
        program_id
)
select
    creation_date,
    count(distinct program_id) as programs
from
    program_creation_date
WHERE
    creation_date :: DATE >= '2022-01-01'
group by
    creation_date
order by
    creation_date ASC;

--
with signers_with_program_id as (
    SELECT
        e.tx_id,
        s.value as signer,
        e.program_id
    FROM
        solana.core.fact_events e
        join solana.core.fact_transactions t on (e.tx_id = t.tx_id),
        lateral flatten(input = > signers) s
    WHERE
        e.block_timestamp :: DATE >= '2022-01-01'
)
select
    program_id,
    count(distinct tx_id) as tx_count,
    count(distinct signer) as signers
from
    signers_with_program_id
group by
    program_id