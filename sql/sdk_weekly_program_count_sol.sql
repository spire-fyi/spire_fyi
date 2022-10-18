SELECT
    DATE_TRUNC(
        week,
        block_timestamp
    ) AS week,
    COUNT(
        DISTINCT program_id
    ) AS unique_programs
FROM
    solana.core.fact_events
WHERE
    succeeded = 'TRUE'
    AND week = {{ date }}
GROUP BY
    week
