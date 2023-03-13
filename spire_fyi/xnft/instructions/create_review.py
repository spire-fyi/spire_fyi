from __future__ import annotations

import typing

import borsh_construct as borsh
from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID

from ..program_id import PROGRAM_ID


class CreateReviewArgs(typing.TypedDict):
    uri: str
    rating: int


layout = borsh.CStruct("uri" / borsh.String, "rating" / borsh.U8)


class CreateReviewAccounts(typing.TypedDict):
    install: Pubkey
    master_token: Pubkey
    xnft: Pubkey
    review: Pubkey
    author: Pubkey


def create_review(
    args: CreateReviewArgs,
    accounts: CreateReviewAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["install"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["master_token"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["xnft"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["review"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["author"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"E\xedW+\xee}(\x01"
    encoded_args = layout.build(
        {
            "uri": args["uri"],
            "rating": args["rating"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
