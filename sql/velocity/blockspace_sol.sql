-- adapted from: charliemarketplace
-- https://app.flipsidecrypto.com/dashboard/ethereum-blockspace-IDa27K
-- query location: https://app.flipsidecrypto.com/velocity/queries/15db0704-70f4-48d5-8ae1-b533dfd99576
WITH block_transactions_gas_events AS (
    SELECT
        block_id,
        block_timestamp,
        COUNT(*) AS num_tx,
        SUM(fee) AS total_gas_used,
        MEDIAN(fee) AS median_gas_price,
        SUM(fee) AS total_gas_revenue --
        -- COUNT(DISTINCT(from_address)) AS num_froms
    FROM
        solana.core.fact_transactions
    WHERE
        block_timestamp :: DATE >= '2022-01-01'
    GROUP BY
        block_id,
        block_timestamp
)
SELECT
    DATE_TRUNC("hour", block_timestamp) AS hour_,
    FLOOR(AVG(num_tx)) AS avg_tx_per_block,
    FLOOR (AVG(total_gas_used)) AS avg_gas_per_block,
    MEDIAN(median_gas_price) AS median_gas_price_per_block,
    FLOOR(AVG(total_gas_revenue)) AS avg_total_gas_revenue,
    AVG(FLOOR(AVG(total_gas_revenue))) over (
        ORDER BY
            hour_ ASC rows BETWEEN 23 preceding
            AND 0 preceding
    ) AS ma24,
    COUNT(block_id) AS num_blocks --
    -- FLOOR(AVG(num_froms)) AS avg_unique_froms_per_block
FROM
    block_transactions_gas_events
GROUP BY
    hour_
ORDER BY
    hour_ ASC;

WITH block_transactions AS (
    SELECT
        block_id,
        block_timestamp,
        COUNT(DISTINCT(s.value)) AS num_froms
    FROM
        solana.core.fact_transactions,
        lateral flatten(input = > signers) s
    WHERE
        block_timestamp :: DATE >= '2022-01-01'
    GROUP BY
        block_id,
        block_timestamp
)
SELECT
    DATE_TRUNC("hour", block_timestamp) AS hour_,
    FLOOR(AVG(num_froms)) AS avg_unique_froms_per_block
FROM
    block_transactions
GROUP BY
    hour_
ORDER BY
    hour_ ASC;

---

