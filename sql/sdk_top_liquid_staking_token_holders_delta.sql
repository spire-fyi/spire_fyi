-- forked from banbannard / Dust Holding Histogram @ https://flipsidecrypto.xyz/banbannard/q/dust-holding-histogram-Ug9DN8
WITH token_holdings AS (
  SELECT
    block_timestamp,
    tx_id,
    post_tokens.value :owner AS wallet,
    post_tokens.value :mint AS token,
    post_tokens.value :accountIndex AS index,
    ZEROIFNULL(post_tokens.value :uiTokenAmount :uiAmount) AS amount,
    ROW_NUMBER() OVER (
      PARTITION BY wallet,
      token
      ORDER BY
        block_id desc,
        tx_id,
        index
    ) AS rn
  FROM
    solana.core.fact_transactions,
    LATERAL FLATTEN(input => post_token_balances) post_tokens
  WHERE
    succeeded = TRUE
    AND post_tokens.value :owner = wallet
    AND post_tokens.value :mint in (
      'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', --mSOL
      '7dHbWXmci3dT8UFYWYZweBLXgycu7Y3iL6trKn1Y7ARj', --stSOL
      'J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', --jitoSOL
      '7Q2afV64in6N6SeZsAAB81TJzwDoD6zpqmHkzi9Dcavn', --jSOL
      '5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', --scnSOL
      'CgnTSoL3DgY9SFHxcLj6CgCgKKoTBr6tp4CPAEWy25DE', --cgntSOL
      'LAinEtNLgpmCP9Rvsf5Hn8W6EhNiKLZQti1xfWMLy6X', --laineSOL
      'bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1', --bSOL
      'GEJpt3Wjmr628FqXxTgxMce1pLntcPV4uFi8ksxMyPQh', --daoSOL
      'BdZPG9xWrG3uFrx2KrUW1jT4tZ9VKPDWknYihzoPRJS3' --prtSOL
    )
    AND block_timestamp::date = {{ date }}
    AND wallet IN ({% for item in wallets -%}
        {% if loop.last -%}
            '{{ item }}'
        {% else %}
            '{{ item }}',
        {%- endif %}
    {%- endfor %})
),
token_holdings_with_prices as (
  select
    block_timestamp::date as "Date",
    wallet,
    token,
    p.token_name,
    p.symbol,
    amount,
    amount * p.close as amount_usd
  FROM
    token_holdings
    LEFT JOIN solana.price.ez_token_prices_hourly p on (
      token = p.token_address
      and date_trunc('hour', block_timestamp) = p.recorded_hour
    )
  WHERE
    rn = 1
)
SELECT
  *
FROM 
  token_holdings_with_prices