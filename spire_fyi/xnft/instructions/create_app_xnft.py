from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class CreateAppXnftArgs(typing.TypedDict):
    name: str
    params: types.create_xnft_params.CreateXnftParams


layout = borsh.CStruct(
    "name" / borsh.String, "params" / types.create_xnft_params.CreateXnftParams.layout
)


class CreateAppXnftAccounts(typing.TypedDict):
    master_mint: Pubkey
    master_token: Pubkey
    master_metadata: Pubkey
    xnft: Pubkey
    payer: Pubkey
    publisher: Pubkey
    metadata_program: Pubkey


def create_app_xnft(
    args: CreateAppXnftArgs,
    accounts: CreateAppXnftAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["master_mint"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["master_token"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["master_metadata"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["xnft"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["payer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["publisher"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["metadata_program"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xa3\xb5*.\xdb\xd3\x07\x85"
    encoded_args = layout.build(
        {
            "name": args["name"],
            "params": args["params"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
