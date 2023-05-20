WITH solana_wallets AS (
    SELECT
        signer as address,
        first_tx_date as creation_date
    FROM
        solana.core.ez_signers
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