-- adapted from: charliemarketplace
-- https://app.flipsidecrypto.com/dashboard/ethereum-blockspace-IDa27K
-- query location: https://app.flipsidecrypto.com/velocity/queries/d24b453e-b709-471a-a48a-c7c25a3ee993
WITH block_transactions_gas_events AS (
    SELECT
        block_number,
        block_timestamp,
        COUNT(*) AS num_tx,
        SUM(gas_used) AS total_gas_used,
        MEDIAN(gas_price) AS median_gas_price,
        SUM(gas_price * gas_used) AS total_gas_revenue,
        COUNT(DISTINCT(from_address)) AS num_froms
    FROM
        ethereum.core.fact_transactions
    WHERE
        block_timestamp :: DATE >= '2022-01-01'
    GROUP BY
        block_number,
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
    COUNT(block_number) AS num_blocks,
    FLOOR(AVG(num_froms)) AS avg_unique_froms_per_block
FROM
    block_transactions_gas_events
GROUP BY
    hour_
ORDER BY
    hour_ ASC;

-- adapted from: charliemarketplace
-- https://app.flipsidecrypto.com/dashboard/ethereum-blockspace-IDa27K
with contract_creates AS (
    SELECT
        DATE_TRUNC("DAY", BLOCK_TIMESTAMP) as day_,
        TX_HASH,
        FROM_ADDRESS as contract_creator,
        TX_JSON :receipt :contractAddress as resulting_contract
    FROM
        ethereum.core.fact_transactions
    WHERE
        BLOCK_NUMBER > 10176000
        AND resulting_contract != 'null'
)
SELECT
    day_,
    COUNT(DISTINCT(resulting_contract)) as num_contracts_created
FROM
    contract_creates
GROUP BY
    day_
ORDER BY
    day_ ASC;