WITH solana_new_wallets AS (
    SELECT
        signer as address,
        first_tx_date as creation_date
    FROM
        solana.core.ez_signers
    WHERE
        creation_date = {{ date }}
)
SELECT
    e.block_timestamp :: DATE AS "Date",
    e.program_id,
    COUNT(DISTINCT e.tx_id) AS tx_count,
    COUNT(DISTINCT s.value) AS signers
FROM
    solana.core.fact_events e
    JOIN solana.core.fact_transactions t
    ON (
        e.tx_id = t.tx_id
        AND e.block_timestamp :: DATE = t.block_timestamp :: DATE
    ),
    lateral flatten(t.signers) as s
WHERE
    e.block_timestamp :: DATE = {{ date }}
    AND s.value IN (
        SELECT
            address
        FROM
            solana_new_wallets
    )
GROUP BY
    program_id,
    "Date"
ORDER BY
    signers