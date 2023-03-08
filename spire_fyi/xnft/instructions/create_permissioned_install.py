from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class CreatePermissionedInstallAccounts(typing.TypedDict):
    xnft: Pubkey
    install_vault: Pubkey
    install: Pubkey
    access: Pubkey
    authority: Pubkey


def create_permissioned_install(
    accounts: CreatePermissionedInstallAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["xnft"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["install_vault"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["install"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["access"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"]\xda\x9d\xd4\x16\x93\xb4\xc4"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
