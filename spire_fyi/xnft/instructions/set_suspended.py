from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class SetSuspendedArgs(typing.TypedDict):
    flag: bool


layout = borsh.CStruct("flag" / borsh.Bool)


class SetSuspendedAccounts(typing.TypedDict):
    xnft: Pubkey
    master_token: Pubkey
    authority: Pubkey


def set_suspended(
    args: SetSuspendedArgs,
    accounts: SetSuspendedAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["xnft"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["master_token"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xf0\xb6\xc8<\xd16\xb4\xf0"
    encoded_args = layout.build(
        {
            "flag": args["flag"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
