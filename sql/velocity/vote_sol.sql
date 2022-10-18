-- tx_count vs vote ratio
-- adapted from: https://app.flipsidecrypto.com/dashboard/NRSsGk
WITH votes AS (
    SELECT
        DATE_TRUNC(
            'hour',
            b.block_timestamp
        ) AS hour_,
        tx_count,
        num_votes,
        num_votes / tx_count AS vote_ratio
    FROM
        solana.core.fact_blocks b
        INNER JOIN solana.core.fact_votes_agg_block v ON (b.block_id = v.block_id)
    WHERE
        b.block_timestamp >= '2022-01-01'
    ORDER BY
        hour_ ASC
)
SELECT
    tx_count,
    avg(num_votes) as avg_votes,
    avg(vote_ratio) as avg_vote_ratio,
    min(vote_ratio) as min_vote_ratio,
    max(vote_ratio) as max_vote_ratio
FROM
    votes
GROUP BY
    tx_count
ORDER BY
    tx_count ASC;

-- hourly vote v non-vote
-- adapted from: https://app.flipsidecrypto.com/dashboard/IbyarV
WITH vote_tx AS (
    SELECT
        b.block_id,
        DATE_TRUNC(
            'hour',
            b.block_timestamp
        ) AS hour_,
        tx_count,
        num_votes,
        num_votes / tx_count AS vote_ratio
    FROM
        solana.core.fact_votes_agg_block v
        JOIN solana.core.fact_blocks b ON v.block_id = b.block_id
    WHERE
        b.block_timestamp >= '2022-01-01'
)
SELECT
    hour_,
    COUNT(block_id) AS blocks,
    SUM(tx_count) AS total_tx,
    SUM(num_votes) AS total_votes,
    total_tx - total_votes AS total_non_vote,
    AVG(tx_count) AS average_tx,
    AVG(num_votes) AS average_votes,
    -- AVG(total_tx - total_votes) AS average_non_vote,
    AVG(vote_ratio) AS avg_block_vote_ratio,
    MIN(vote_ratio) AS minimum_block_vote_ratio,
    MAX(vote_ratio) AS maximum_block_vote_ratio,
    total_votes / total_tx AS avg_hourly_vote_ratio
FROM
    vote_tx
GROUP BY
    hour_
ORDER BY
    hour_ ASC;

-- vote distribution
-- adapted from: https://app.flipsidecrypto.com/dashboard/IbyarV
WITH vote_tx AS (
    SELECT
        b.block_id,
        b.block_timestamp,
        tx_count,
        num_votes,
        num_votes / tx_count AS vote_ratio
    FROM
        solana.core.fact_votes_agg_block v
        JOIN solana.core.fact_blocks b ON v.block_id = b.block_id
)
SELECT
    ROUND(vote_ratio) AS vote_percent,
    COUNT(DISTINCT block_id) AS blocks
FROM
    vote_tx
WHERE
    b.block_timestamp >= '2022-01-01'
GROUP BY
    vote_percent
ORDER BY
    vote_percent;