SELECT
    DISTINCT signers [0] AS addresses,
    MIN(DATE(block_timestamp)) AS first_active_date
FROM
    solana.core.fact_transactions
GROUP BY
    signers
HAVING
    first_active_date = {{ date }}
