from __future__ import annotations

import typing

from dataclasses import dataclass

import borsh_construct as borsh
from anchorpy.borsh_extension import BorshPubkey
from construct import Container
from solders.pubkey import Pubkey

from . import tag


class UpdateParamsJSON(typing.TypedDict):
    install_authority: typing.Optional[str]
    install_price: int
    install_vault: str
    name: typing.Optional[str]
    supply: typing.Optional[int]
    tag: tag.TagJSON
    uri: typing.Optional[str]


@dataclass
class UpdateParams:
    layout: typing.ClassVar = borsh.CStruct(
        "install_authority" / borsh.Option(BorshPubkey),
        "install_price" / borsh.U64,
        "install_vault" / BorshPubkey,
        "name" / borsh.Option(borsh.String),
        "supply" / borsh.Option(borsh.U64),
        "tag" / tag.layout,
        "uri" / borsh.Option(borsh.String),
    )
    install_authority: typing.Optional[Pubkey]
    install_price: int
    install_vault: Pubkey
    name: typing.Optional[str]
    supply: typing.Optional[int]
    tag: tag.TagKind
    uri: typing.Optional[str]

    @classmethod
    def from_decoded(cls, obj: Container) -> "UpdateParams":
        return cls(
            install_authority=obj.install_authority,
            install_price=obj.install_price,
            install_vault=obj.install_vault,
            name=obj.name,
            supply=obj.supply,
            tag=tag.from_decoded(obj.tag),
            uri=obj.uri,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "install_authority": self.install_authority,
            "install_price": self.install_price,
            "install_vault": self.install_vault,
            "name": self.name,
            "supply": self.supply,
            "tag": self.tag.to_encodable(),
            "uri": self.uri,
        }

    def to_json(self) -> UpdateParamsJSON:
        return {
            "install_authority": (None if self.install_authority is None else str(self.install_authority)),
            "install_price": self.install_price,
            "install_vault": str(self.install_vault),
            "name": self.name,
            "supply": self.supply,
            "tag": self.tag.to_json(),
            "uri": self.uri,
        }

    @classmethod
    def from_json(cls, obj: UpdateParamsJSON) -> "UpdateParams":
        return cls(
            install_authority=(
                None if obj["install_authority"] is None else Pubkey.from_string(obj["install_authority"])
            ),
            install_price=obj["install_price"],
            install_vault=Pubkey.from_string(obj["install_vault"]),
            name=obj["name"],
            supply=obj["supply"],
            tag=tag.from_json(obj["tag"]),
            uri=obj["uri"],
        )
