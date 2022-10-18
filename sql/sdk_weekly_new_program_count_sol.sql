WITH first_program_tx AS (
    SELECT
        program_id,
        MIN(
            DATE_TRUNC(
                week,
                block_timestamp
            )
        ) AS program_first_tx
    FROM
        solana.core.fact_events
    WHERE
        succeeded = 'TRUE'
    GROUP BY
        program_id
),
new_programs AS (
    SELECT
        program_first_tx AS week,
        COUNT(
            DISTINCT program_id
        ) AS "New Programs"
    FROM
        first_program_tx
    WHERE
        week = {{ date }}
    GROUP BY
        week
)
SELECT
    *
FROM
    new_programs
