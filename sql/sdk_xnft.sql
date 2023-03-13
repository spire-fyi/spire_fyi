select
    block_timestamp,
    block_id,
    tx_id,
    instructions [0] :accounts [0] as xnft,
    -- only the xNFT account for certain instructions
    instructions [0] :data as program_data,
    -- can be used to find instruction name 
    case
        when program_data = '7tyNegi96Ez' then 'createInstall'
        else program_data
    end as instruction_type,
    instructions [0] :programId as programId,
    signers [0] as fee_payer,
    succeeded,
    instructions [0] :accounts as all_accounts -- unparsed account info
from
    solana.core.fact_transactions
where
    programId = 'xnft5aaToUM4UFETUQfj7NUDUBdvYHTVhNFThEYTm55'
    and block_timestamp :: date > {{ date }}
order by
    block_timestamp desc