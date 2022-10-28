SELECT
    DATE_TRUNC(
        week,
        block_timestamp
    ) AS week,
    COUNT(
        DISTINCT signers [0]
    ) AS unique_users
FROM
    solana.core.fact_transactions
WHERE
    week = {{ date }}
GROUP BY
    week
