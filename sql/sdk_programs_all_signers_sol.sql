SELECT
    e.block_timestamp :: DATE AS "Date",
    e.program_id,
    COUNT(
        DISTINCT e.tx_id
    ) AS tx_count,
    COUNT(
        DISTINCT s.value
    ) AS signers
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
GROUP BY
    program_id,
    "Date"
ORDER BY
    signers
