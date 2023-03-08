from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class VerifyCuratorAccounts(typing.TypedDict):
    xnft: Pubkey
    curator: Pubkey


def verify_curator(
    accounts: VerifyCuratorAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["xnft"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["curator"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\r~\r j\x07\xad\x95"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
