from __future__ import annotations

import typing

import borsh_construct as borsh
from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey

from .. import types
from ..program_id import PROGRAM_ID


class UpdateXnftArgs(typing.TypedDict):
    updates: types.update_params.UpdateParams


layout = borsh.CStruct("updates" / types.update_params.UpdateParams.layout)


class UpdateXnftAccounts(typing.TypedDict):
    xnft: Pubkey
    master_token: Pubkey
    master_metadata: Pubkey
    curation_authority: Pubkey
    updater: Pubkey
    metadata_program: Pubkey


def update_xnft(
    args: UpdateXnftArgs,
    accounts: UpdateXnftAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["xnft"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["master_token"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["master_metadata"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["curation_authority"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["updater"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["metadata_program"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"A\xd3\xd4\x93\xef\x9a\x85\x02"
    encoded_args = layout.build(
        {
            "updates": args["updates"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
