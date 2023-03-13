from __future__ import annotations

import typing

from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey

from ..program_id import PROGRAM_ID


class DeleteInstallAccounts(typing.TypedDict):
    install: Pubkey
    receiver: Pubkey
    authority: Pubkey


def delete_install(
    accounts: DeleteInstallAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["install"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["receiver"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xdf\x86~\x01\xb7\x1a\xfe\xce"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
