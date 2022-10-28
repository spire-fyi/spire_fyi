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
        count(address) as new_users,
        DATE_TRUNC(
            week,
            creation_date
        ) AS week
    FROM
        solana_wallets
    WHERE
        week = {{ date }}
    GROUP BY 
        week
)
SELECT
    *
FROM
    solana_new_wallets