from __future__ import annotations

import typing

from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID

from ..program_id import PROGRAM_ID


class TransferAccounts(typing.TypedDict):
    xnft: Pubkey
    source: Pubkey
    destination: Pubkey
    master_mint: Pubkey
    recipient: Pubkey
    authority: Pubkey


def transfer(
    accounts: TransferAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["xnft"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["source"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["destination"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["master_mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["recipient"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xa34\xc8\xe7\x8c\x03E\xba"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
