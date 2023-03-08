import typing
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import PROGRAM_ID


class ReviewJSON(typing.TypedDict):
    author: str
    xnft: str
    rating: int
    uri: str
    reserved: list[int]


@dataclass
class Review:
    discriminator: typing.ClassVar = b"|?\xcb\xd7\xe2\x1e\xde\x0f"
    layout: typing.ClassVar = borsh.CStruct(
        "author" / BorshPubkey,
        "xnft" / BorshPubkey,
        "rating" / borsh.U8,
        "uri" / borsh.String,
        "reserved" / borsh.U8[32],
    )
    author: Pubkey
    xnft: Pubkey
    rating: int
    uri: str
    reserved: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["Review"]:
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
    ) -> typing.List[typing.Optional["Review"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Review"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Review":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = Review.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            author=dec.author,
            xnft=dec.xnft,
            rating=dec.rating,
            uri=dec.uri,
            reserved=dec.reserved,
        )

    def to_json(self) -> ReviewJSON:
        return {
            "author": str(self.author),
            "xnft": str(self.xnft),
            "rating": self.rating,
            "uri": self.uri,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: ReviewJSON) -> "Review":
        return cls(
            author=Pubkey.from_string(obj["author"]),
            xnft=Pubkey.from_string(obj["xnft"]),
            rating=obj["rating"],
            uri=obj["uri"],
            reserved=obj["reserved"],
        )
