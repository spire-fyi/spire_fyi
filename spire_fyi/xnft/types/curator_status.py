from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class CuratorStatusJSON(typing.TypedDict):
    pubkey: str
    verified: bool


@dataclass
class CuratorStatus:
    layout: typing.ClassVar = borsh.CStruct(
        "pubkey" / BorshPubkey, "verified" / borsh.Bool
    )
    pubkey: Pubkey
    verified: bool

    @classmethod
    def from_decoded(cls, obj: Container) -> "CuratorStatus":
        return cls(pubkey=obj.pubkey, verified=obj.verified)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"pubkey": self.pubkey, "verified": self.verified}

    def to_json(self) -> CuratorStatusJSON:
        return {"pubkey": str(self.pubkey), "verified": self.verified}

    @classmethod
    def from_json(cls, obj: CuratorStatusJSON) -> "CuratorStatus":
        return cls(pubkey=Pubkey.from_string(obj["pubkey"]), verified=obj["verified"])
