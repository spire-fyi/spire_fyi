WITH solana_new_wallets AS (
    SELECT
        *
    FROM
        solana.core.ez_signers
    WHERE
        first_tx_date = {{ date }}
)
SELECT
    DISTINCT e.program_id AS program_id,
    t.signers [0] :: STRING AS signers
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
    AND t.signers [0]::string IN (
        SELECT
            signer
        FROM
            solana_new_wallets
    )
