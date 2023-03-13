import typing

from dataclasses import dataclass

import borsh_construct as borsh
from anchorpy.borsh_extension import BorshPubkey
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solders.pubkey import Pubkey

from ..program_id import PROGRAM_ID


class AccessJSON(typing.TypedDict):
    wallet: str
    xnft: str
    bump: int
    reserved: list[int]


@dataclass
class Access:
    discriminator: typing.ClassVar = b"u\x9al\xd2\xcaS`\xde"
    layout: typing.ClassVar = borsh.CStruct(
        "wallet" / BorshPubkey,
        "xnft" / BorshPubkey,
        "bump" / borsh.U8,
        "reserved" / borsh.U8[32],
    )
    wallet: Pubkey
    xnft: Pubkey
    bump: int
    reserved: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["Access"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp.value
        if info is None:
            return None
        if info.owner != program_id:
            raise ValueError("Account does not belong to this program")
        bytes_data = info.data
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[Pubkey],
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.List[typing.Optional["Access"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Access"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Access":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator("The discriminator for this account is invalid")
        dec = Access.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            wallet=dec.wallet,
            xnft=dec.xnft,
            bump=dec.bump,
            reserved=dec.reserved,
        )

    def to_json(self) -> AccessJSON:
        return {
            "wallet": str(self.wallet),
            "xnft": str(self.xnft),
            "bump": self.bump,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: AccessJSON) -> "Access":
        return cls(
            wallet=Pubkey.from_string(obj["wallet"]),
            xnft=Pubkey.from_string(obj["xnft"]),
            bump=obj["bump"],
            reserved=obj["reserved"],
        )
