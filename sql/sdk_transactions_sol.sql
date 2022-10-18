WITH consumption_tx AS (
    SELECT
        t.block_timestamp,
        t.tx_id,
        t.fee,
        t.succeeded,
        SUM(
            SPLIT(
                REGEXP_SUBSTR(
                    s.value,
                    '[0-9]* of [0-9]*'
                ),
                ' of '
            ) [0] :: INT
        ) AS compute_units_used,
        AVG(
            SPLIT(
                REGEXP_SUBSTR(
                    s.value,
                    '[0-9]* of [0-9]*'
                ),
                ' of '
            ) [1] :: INT
        ) AS avg_compute_units_requested,
        AVG(
            CASE
                WHEN SPLIT(
                    REGEXP_SUBSTR(
                        s.value,
                        '[0-9]* of [0-9]*'
                    ),
                    ' of '
                ) [1] :: INT = 0 THEN NULL
                ELSE SPLIT(
                    REGEXP_SUBSTR(
                        s.value,
                        '[0-9]* of [0-9]*'
                    ),
                    ' of '
                ) [0] :: INT / SPLIT(
                    REGEXP_SUBSTR(
                        s.value,
                        '[0-9]* of [0-9]*'
                    ),
                    ' of '
                ) [1] :: INT
            END
        ) AS avg_compute_units_proportion
    FROM
        solana.core.fact_transactions t,
        LATERAL FLATTEN(
            input => t.log_messages
        ) s
    WHERE
        block_timestamp :: DATE = {{ date }}
        AND s.value LIKE '% consumed %'
    GROUP BY
        t.block_timestamp,
        t.tx_id,
        t.fee,
        t.succeeded
)
SELECT
    DATE_TRUNC(
        'hour',
        block_timestamp
    ) AS datetime,
    -- total tx
    COUNT(tx_id) AS total_tx,
    SUM(fee) AS total_fee,
    AVG(fee) AS avg_total_fee,
    SUM(compute_units_used) AS total_compute_units_used,
    AVG(compute_units_used) AS total_avg_compute_units_used,
    AVG(avg_compute_units_requested) AS total_avg_compute_units_requested,
    AVG(avg_compute_units_proportion) AS total_avg_compute_units_proportion,
    -- successful tx:
    COUNT(
        CASE
            WHEN succeeded = 'TRUE' THEN succeeded
            ELSE NULL
        END
    ) AS successful_tx,
    SUM(
        CASE
            WHEN succeeded = 'TRUE' THEN fee
            ELSE NULL
        END
    ) AS successful_fee,
    AVG(
        CASE
            WHEN succeeded = 'TRUE' THEN fee
            ELSE NULL
        END
    ) AS avg_successful_fee,
    SUM(
        CASE
            WHEN succeeded = 'TRUE' THEN compute_units_used
            ELSE NULL
        END
    ) AS successful_compute_units_used,
    AVG(
        CASE
            WHEN succeeded = 'TRUE' THEN compute_units_used
            ELSE NULL
        END
    ) AS avg_successful_compute_units_used,
    AVG(
        CASE
            WHEN succeeded = 'TRUE' THEN avg_compute_units_requested
            ELSE NULL
        END
    ) AS avg_successful_compute_units_requested,
    AVG(
        CASE
            WHEN succeeded = 'TRUE' THEN avg_compute_units_proportion
            ELSE NULL
        END
    ) AS avg_successful_compute_units_proportion,
    -- failed tx:
    COUNT(
        CASE
            WHEN succeeded = 'FALSE' THEN succeeded
            ELSE NULL
        END
    ) AS failed_tx,
    SUM(
        CASE
            WHEN succeeded = 'FALSE' THEN fee
            ELSE NULL
        END
    ) AS failed_fee,
    AVG(
        CASE
            WHEN succeeded = 'FALSE' THEN fee
            ELSE NULL
        END
    ) AS avg_failed_fee,
    SUM(
        CASE
            WHEN succeeded = 'FALSE' THEN compute_units_used
            ELSE NULL
        END
    ) AS failed_compute_units_used,
    AVG(
        CASE
            WHEN succeeded = 'FALSE' THEN compute_units_used
            ELSE NULL
        END
    ) AS avg_failed_compute_units_used,
    AVG(
        CASE
            WHEN succeeded = 'FALSE' THEN avg_compute_units_requested
            ELSE NULL
        END
    ) AS avg_failed_compute_units_requested,
    AVG(
        CASE
            WHEN succeeded = 'FALSE' THEN avg_compute_units_proportion
            ELSE NULL
        END
    ) AS avg_failed_compute_units_proportion,
    -- rates:
    CASE
        WHEN total_tx = 0 THEN NULL
        ELSE successful_tx / total_tx
    END AS success_rate,
    total_tx / 3600 AS total_tps,
    successful_tx / 3600 AS succesful_tps,
    failed_tx / 3600 AS failed_tps
FROM
    consumption_tx
GROUP BY
    datetime
ORDER BY
    datetime
