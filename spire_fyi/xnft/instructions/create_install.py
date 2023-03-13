from __future__ import annotations

import typing

from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID

from ..program_id import PROGRAM_ID


class CreateInstallAccounts(typing.TypedDict):
    xnft: Pubkey
    install_vault: Pubkey
    install: Pubkey
    authority: Pubkey
    target: Pubkey


def create_install(
    accounts: CreateInstallAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["xnft"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["install_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["install"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["target"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"):\x99\t\xe4;\xda\xcf"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
