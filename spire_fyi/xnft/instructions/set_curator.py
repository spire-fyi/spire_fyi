from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class SetCuratorAccounts(typing.TypedDict):
    xnft: Pubkey
    master_token: Pubkey
    curator: Pubkey
    authority: Pubkey


def set_curator(
    accounts: SetCuratorAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["xnft"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["master_token"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["curator"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"s\x7f\xc4\xdb\xeb\xc6`\xfd"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
