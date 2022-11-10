SELECT
    DISTINCT e.program_id AS program_id,
    t.signers [0] AS signers
FROM
    solana.core.fact_events e
    JOIN solana.core.fact_transactions t
    ON (
        e.tx_id = t.tx_id
        AND e.block_timestamp :: DATE = t.block_timestamp :: DATE
    )
WHERE
    e.block_timestamp :: DATE = {{ date }}
    AND e.program_id = {{ program_id }}
ORDER BY
    program_id
