select
    block_timestamp,
    tx_id,
    purchaser,
    seller,
    mint,
    sales_amount
from
    solana.nft.fact_nft_sales
where
    PROGRAM_ID = 'M2mx93ekt1fmXSVkTrUL9xVFHkmME8HTUi5Cyc5aF7K'
    and succeeded = 'True'
    and date_trunc('hour', block_timestamp) = {{ date }}