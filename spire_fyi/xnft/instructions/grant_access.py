from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class GrantAccessAccounts(typing.TypedDict):
    xnft: Pubkey
    wallet: Pubkey
    access: Pubkey
    authority: Pubkey


def grant_access(
    accounts: GrantAccessAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["xnft"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["wallet"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["access"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"BXWq'\x16\x1b\xa5"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
