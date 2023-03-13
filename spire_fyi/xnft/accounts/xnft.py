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

from .. import types
from ..program_id import PROGRAM_ID


class XnftJSON(typing.TypedDict):
    publisher: str
    install_vault: str
    master_metadata: str
    master_mint: str
    install_authority: typing.Optional[str]
    curator: typing.Optional[types.curator_status.CuratorStatusJSON]
    uri: str
    mint_seed_name: typing.Optional[str]
    kind: types.kind.KindJSON
    tag: types.tag.TagJSON
    supply: typing.Optional[int]
    total_installs: int
    install_price: int
    created_ts: int
    updated_ts: int
    total_rating: int
    num_ratings: int
    suspended: bool
    bump: list[int]
    reserved0: list[int]
    reserved1: list[int]
    reserved2: list[int]


@dataclass
class Xnft:
    discriminator: typing.ClassVar = b"\xb0\xe4\xe4\xa5\x97\xfeX\xde"
    layout: typing.ClassVar = borsh.CStruct(
        "publisher" / BorshPubkey,
        "install_vault" / BorshPubkey,
        "master_metadata" / BorshPubkey,
        "master_mint" / BorshPubkey,
        "install_authority" / borsh.Option(BorshPubkey),
        "curator" / borsh.Option(types.curator_status.CuratorStatus.layout),
        "uri" / borsh.String,
        "mint_seed_name" / borsh.Option(borsh.String),
        "kind" / types.kind.layout,
        "tag" / types.tag.layout,
        "supply" / borsh.Option(borsh.U64),
        "total_installs" / borsh.U64,
        "install_price" / borsh.U64,
        "created_ts" / borsh.I64,
        "updated_ts" / borsh.I64,
        "total_rating" / borsh.U64,
        "num_ratings" / borsh.U32,
        "suspended" / borsh.Bool,
        "bump" / borsh.U8[1],
        "reserved0" / borsh.U8[64],
        "reserved1" / borsh.U8[24],
        "reserved2" / borsh.U8[9],
    )
    publisher: Pubkey
    install_vault: Pubkey
    master_metadata: Pubkey
    master_mint: Pubkey
    install_authority: typing.Optional[Pubkey]
    curator: typing.Optional[types.curator_status.CuratorStatus]
    uri: str
    mint_seed_name: typing.Optional[str]
    kind: types.kind.KindKind
    tag: types.tag.TagKind
    supply: typing.Optional[int]
    total_installs: int
    install_price: int
    created_ts: int
    updated_ts: int
    total_rating: int
    num_ratings: int
    suspended: bool
    bump: list[int]
    reserved0: list[int]
    reserved1: list[int]
    reserved2: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["Xnft"]:
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
    ) -> typing.List[typing.Optional["Xnft"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Xnft"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Xnft":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator("The discriminator for this account is invalid")
        dec = Xnft.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            publisher=dec.publisher,
            install_vault=dec.install_vault,
            master_metadata=dec.master_metadata,
            master_mint=dec.master_mint,
            install_authority=dec.install_authority,
            curator=(
                None if dec.curator is None else types.curator_status.CuratorStatus.from_decoded(dec.curator)
            ),
            uri=dec.uri,
            mint_seed_name=dec.mint_seed_name,
            kind=types.kind.from_decoded(dec.kind),
            tag=types.tag.from_decoded(dec.tag),
            supply=dec.supply,
            total_installs=dec.total_installs,
            install_price=dec.install_price,
            created_ts=dec.created_ts,
            updated_ts=dec.updated_ts,
            total_rating=dec.total_rating,
            num_ratings=dec.num_ratings,
            suspended=dec.suspended,
            bump=dec.bump,
            reserved0=dec.reserved0,
            reserved1=dec.reserved1,
            reserved2=dec.reserved2,
        )

    def to_json(self) -> XnftJSON:
        return {
            "publisher": str(self.publisher),
            "install_vault": str(self.install_vault),
            "master_metadata": str(self.master_metadata),
            "master_mint": str(self.master_mint),
            "install_authority": (None if self.install_authority is None else str(self.install_authority)),
            "curator": (None if self.curator is None else self.curator.to_json()),
            "uri": self.uri,
            "mint_seed_name": self.mint_seed_name,
            "kind": self.kind.to_json(),
            "tag": self.tag.to_json(),
            "supply": self.supply,
            "total_installs": self.total_installs,
            "install_price": self.install_price,
            "created_ts": self.created_ts,
            "updated_ts": self.updated_ts,
            "total_rating": self.total_rating,
            "num_ratings": self.num_ratings,
            "suspended": self.suspended,
            "bump": self.bump,
            "reserved0": self.reserved0,
            "reserved1": self.reserved1,
            "reserved2": self.reserved2,
        }

    @classmethod
    def from_json(cls, obj: XnftJSON) -> "Xnft":
        return cls(
            publisher=Pubkey.from_string(obj["publisher"]),
            install_vault=Pubkey.from_string(obj["install_vault"]),
            master_metadata=Pubkey.from_string(obj["master_metadata"]),
            master_mint=Pubkey.from_string(obj["master_mint"]),
            install_authority=(
                None if obj["install_authority"] is None else Pubkey.from_string(obj["install_authority"])
            ),
            curator=(
                None
                if obj["curator"] is None
                else types.curator_status.CuratorStatus.from_json(obj["curator"])
            ),
            uri=obj["uri"],
            mint_seed_name=obj["mint_seed_name"],
            kind=types.kind.from_json(obj["kind"]),
            tag=types.tag.from_json(obj["tag"]),
            supply=obj["supply"],
            total_installs=obj["total_installs"],
            install_price=obj["install_price"],
            created_ts=obj["created_ts"],
            updated_ts=obj["updated_ts"],
            total_rating=obj["total_rating"],
            num_ratings=obj["num_ratings"],
            suspended=obj["suspended"],
            bump=obj["bump"],
            reserved0=obj["reserved0"],
            reserved1=obj["reserved1"],
            reserved2=obj["reserved2"],
        )
