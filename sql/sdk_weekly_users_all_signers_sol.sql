SELECT
    DATE_TRUNC(
        week,
        block_timestamp
    ) AS week,
    COUNT(
        DISTINCT s.value
    ) AS unique_users
FROM
    solana.core.fact_transactions,
    lateral flatten(signers) as s
WHERE
    week = {{ date }}
GROUP BY
    week
