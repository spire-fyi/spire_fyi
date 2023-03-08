from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class DeleteReviewAccounts(typing.TypedDict):
    review: Pubkey
    xnft: Pubkey
    receiver: Pubkey
    author: Pubkey


def delete_review(
    accounts: DeleteReviewAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["review"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["xnft"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["receiver"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["author"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xd9e\nG\xe7\xdc\xf1\xca"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
