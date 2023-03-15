with first_tx as (
    select
        signers [0] as wallet,
        min(date(block_timestamp)) as first_tx_date,
        program_id,
        CASE
            WHEN program_id IN (
                'mv3ekLzLbnVPNxjSKvqBpU3ZeZXPQdEC3bp5MDEBG68',
                '5fNfvyp5czQVX77yoACa3JJVEhdRaWjPuazuWgjhTqEH',
                'JD3bq9hGdy38PuWQ4h2YJpELmHVGPPfFSuFkpzAd9zfu'
            ) THEN 'Mango Markets'
            WHEN program_id IN (
                'J2NhFnBxcwbxovE7avBQCXWPgfVtxi5sJfz68AH6R2Mg',
                '9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin',
                '22Y43yTVxuUkoRKdm9thyRhQ3SdgQS7c7kB6UNCiaczD',
                'EUqojwWA2rd19FZrzeBncJsm38Jm1hEhE3zsmX3bRc2o',
                'BJ3jrUzddfuSrZHXSCxMUUQsjKEyLmuuyZebkcaFp2fg',
                '4ckmDgGdxQoPDLUkDT3vHgSAkzA3QRdNq5ywwY4sUSJn'
            ) THEN 'Serum'
            WHEN program_id = 'srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX' THEN 'Openbook'
            WHEN program_id IN (
                'AMM55ShdkoGRB5jVYPjWziwk8m5MpwyDgsMWHaMSQWH6',
                'CURVGoZn8zycx6FXwwevgBTB2gVvdbGTEpvMJDbgs2t4'
            ) THEN 'Aldrin'
            WHEN program_id IN (
                'JUP6i4ozu5ydDCnLiMogSckDPpbtr7BJ4FtzYWkb5Rk',
                'JUP2jxvXaqu7NQY1GmNF4m1vodw12LVXYxbFL2uJvfo',
                'JUP3c2Uh3WA4Ng34tw6kPd2G4C5BB21Xo36Je1s32Ph',
                'JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB'
            ) THEN 'Jupiter Aggregator'
            WHEN program_id IN (
                'RVKd61ztZW9GUwhRbbLoYVRE5Xf1B2tVscKqwZqXgEr',
                '27haf8L6oxUeXrHrgEgsexjSY5hbVUWEmvv9Nyxg8vQv',
                '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8',
                'CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK'
            ) THEN 'Raydium'
            WHEN program_id = 'SSwpkEEcbUqx4vtoEByFjSkhKdCT862DNVb52nZg1UZ' THEN 'Saber'
            WHEN program_id = 'MERLuDFBMmsHnsBPZw2sDQZHvXFMwp8EdjudcU2HKky' THEN 'Mercurial'
            WHEN program_id IN (
                'DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1',
                'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc',
                '9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP'
            ) THEN 'Orca'
            WHEN program_id = 'SSwpMgqNDsyV7mAgN9ady4bDVu5ySjmmXejXvy2vLt1' THEN 'Step Finance'
            WHEN program_id = 'cysPXAjehMpVKUapzbMCCnpFxUFFryEWEaLgnb9NrR8' THEN 'Cykura'
            WHEN program_id = '6MLxLqiXaaSUpkgMnWDTuejNZEz3kE7k2woyHGVFw319' THEN 'Crema'
            WHEN program_id = 'EewxydAPCCVuNEyrVN68PuSYdQ7wKn27V9Gjeoi8dy3S' THEN 'Lifinity'
            WHEN program_id = 'Dooar9JkhdZ7J3LHN3A7YCuoGRUggXhQaG4kijfLGU2j' THEN 'Stepn'
            WHEN program_id = 'HyaB3W9q6XdA5xwpU4XnSZV94htfmbmqJXZcEbRaJutt' THEN 'Invariant'
            WHEN program_id = '7WduLbRfYhTJktjLw5FDEyrqoEv61aTTCuGAetgLjzN5' THEN 'GooseFX'
            ELSE NULL
        end as dex
    from
        solana.core.fact_events
    where
        program_id = {{ program_id }}
    group by
        wallet,
        program_id,
        dex
),
new_wallets AS (
    SELECT
        first_tx_date,
        count(distinct wallet) as new_wallets,
        program_id,
        dex        
    FROM
        first_tx
    WHERE
        first_tx_date = {{ date }}

    GROUP BY
        first_tx_date,
        program_id,
        dex
)
select
    *
from
    new_wallets