from __future__ import annotations

import typing

from dataclasses import dataclass

import borsh_construct as borsh
from anchorpy.borsh_extension import BorshPubkey
from construct import Container
from solders.pubkey import Pubkey


class CreatorsParamJSON(typing.TypedDict):
    address: str
    share: int


@dataclass
class CreatorsParam:
    layout: typing.ClassVar = borsh.CStruct("address" / BorshPubkey, "share" / borsh.U8)
    address: Pubkey
    share: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "CreatorsParam":
        return cls(address=obj.address, share=obj.share)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"address": self.address, "share": self.share}

    def to_json(self) -> CreatorsParamJSON:
        return {"address": str(self.address), "share": self.share}

    @classmethod
    def from_json(cls, obj: CreatorsParamJSON) -> "CreatorsParam":
        return cls(address=Pubkey.from_string(obj["address"]), share=obj["share"])
