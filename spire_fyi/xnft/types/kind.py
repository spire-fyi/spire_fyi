from __future__ import annotations

import typing

from dataclasses import dataclass

import borsh_construct as borsh
from anchorpy.borsh_extension import EnumForCodegen


class AppJSON(typing.TypedDict):
    kind: typing.Literal["App"]


class CollectibleJSON(typing.TypedDict):
    kind: typing.Literal["Collectible"]


@dataclass
class App:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "App"

    @classmethod
    def to_json(cls) -> AppJSON:
        return AppJSON(
            kind="App",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "App": {},
        }


@dataclass
class Collectible:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Collectible"

    @classmethod
    def to_json(cls) -> CollectibleJSON:
        return CollectibleJSON(
            kind="Collectible",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Collectible": {},
        }


KindKind = typing.Union[App, Collectible]
KindJSON = typing.Union[AppJSON, CollectibleJSON]


def from_decoded(obj: dict) -> KindKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "App" in obj:
        return App()
    if "Collectible" in obj:
        return Collectible()
    raise ValueError("Invalid enum object")


def from_json(obj: KindJSON) -> KindKind:
    if obj["kind"] == "App":
        return App()
    if obj["kind"] == "Collectible":
        return Collectible()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen("App" / borsh.CStruct(), "Collectible" / borsh.CStruct())
