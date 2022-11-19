WITH solana_wallets AS (
    SELECT
        signers [0] AS address,
        MIN(DATE(block_timestamp)) AS creation_date
    FROM
        solana.core.fact_transactions
    GROUP BY
        address
),
solana_new_wallets AS (
    SELECT
        address,
        creation_date
    FROM
        solana_wallets
    WHERE
        creation_date = {{ date }}
)
SELECT
    e.block_timestamp :: DATE AS "Date",
    e.program_id,
    COUNT(DISTINCT e.tx_id) AS tx_count,
    COUNT(DISTINCT t.signers [0]) AS signers
FROM
    solana.core.fact_events e
    JOIN solana.core.fact_transactions t
    ON (
        e.tx_id = t.tx_id
        AND e.block_timestamp :: DATE = t.block_timestamp :: DATE
    )
WHERE
    e.block_timestamp :: DATE = {{ date }}
    AND t.signers [0] IN (
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