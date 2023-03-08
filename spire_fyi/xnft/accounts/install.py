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


class InstallJSON(typing.TypedDict):
    authority: str
    xnft: str
    master_metadata: str
    edition: int
    reserved: list[int]


@dataclass
class Install:
    discriminator: typing.ClassVar = b"\xc9\xe8\xf1\xcb\xdcDY/"
    layout: typing.ClassVar = borsh.CStruct(
        "authority" / BorshPubkey,
        "xnft" / BorshPubkey,
        "master_metadata" / BorshPubkey,
        "edition" / borsh.U64,
        "reserved" / borsh.U8[64],
    )
    authority: Pubkey
    xnft: Pubkey
    master_metadata: Pubkey
    edition: int
    reserved: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["Install"]:
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
    ) -> typing.List[typing.Optional["Install"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Install"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Install":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = Install.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            authority=dec.authority,
            xnft=dec.xnft,
            master_metadata=dec.master_metadata,
            edition=dec.edition,
            reserved=dec.reserved,
        )

    def to_json(self) -> InstallJSON:
        return {
            "authority": str(self.authority),
            "xnft": str(self.xnft),
            "master_metadata": str(self.master_metadata),
            "edition": self.edition,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: InstallJSON) -> "Install":
        return cls(
            authority=Pubkey.from_string(obj["authority"]),
            xnft=Pubkey.from_string(obj["xnft"]),
            master_metadata=Pubkey.from_string(obj["master_metadata"]),
            edition=obj["edition"],
            reserved=obj["reserved"],
        )
