from __future__ import annotations

import typing

from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey

from ..program_id import PROGRAM_ID


class RevokeAccessAccounts(typing.TypedDict):
    xnft: Pubkey
    wallet: Pubkey
    access: Pubkey
    authority: Pubkey


def revoke_access(
    accounts: RevokeAccessAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["xnft"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["wallet"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["access"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"j\x80&\xa9g\xeef\x93"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
