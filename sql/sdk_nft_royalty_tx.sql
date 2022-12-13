WITH royalty_payments AS (
    SELECT
        *
    FROM
        solana.core.fact_transfers
    WHERE
        mint = 'So11111111111111111111111111111111111111112'
        AND tx_to = {{ creator_address }}
        AND block_timestamp :: DATE >= '2022-10-07'
)
SELECT
    s.block_timestamp,
    s.tx_id,
    s.marketplace,
    s.mint,
    s.sales_amount,
    COALESCE(
        t.amount,
        0
    ) AS royalty_amount
FROM
    solana.core.fact_nft_sales s
    LEFT JOIN royalty_payments t
    ON (
        s.block_timestamp = t.block_timestamp
        AND s.tx_id = t.tx_id
        AND t.mint = 'So11111111111111111111111111111111111111112'
        AND t.tx_to = {{ creator_address }}
    )
WHERE
    s.block_timestamp :: DATE >= '2022-10-07'
    AND s.succeeded='TRUE'
    AND s.mint IN ({% for item in mints -%}
        {% if loop.last -%}
            '{{ item }}'
        {% else %}
            '{{ item }}',
        {%- endif %}
    {%- endfor %})
ORDER BY
    s.block_timestamp