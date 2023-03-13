from __future__ import annotations

import typing

from dataclasses import dataclass

import borsh_construct as borsh
from anchorpy.borsh_extension import EnumForCodegen


class NoneJSON(typing.TypedDict):
    kind: typing.Literal["None"]


class DefiJSON(typing.TypedDict):
    kind: typing.Literal["Defi"]


class GameJSON(typing.TypedDict):
    kind: typing.Literal["Game"]


class NftsJSON(typing.TypedDict):
    kind: typing.Literal["Nfts"]


@dataclass
class None_:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "None"

    @classmethod
    def to_json(cls) -> NoneJSON:
        return NoneJSON(
            kind="None",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "None": {},
        }


@dataclass
class Defi:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Defi"

    @classmethod
    def to_json(cls) -> DefiJSON:
        return DefiJSON(
            kind="Defi",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Defi": {},
        }


@dataclass
class Game:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "Game"

    @classmethod
    def to_json(cls) -> GameJSON:
        return GameJSON(
            kind="Game",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Game": {},
        }


@dataclass
class Nfts:
    discriminator: typing.ClassVar = 3
    kind: typing.ClassVar = "Nfts"

    @classmethod
    def to_json(cls) -> NftsJSON:
        return NftsJSON(
            kind="Nfts",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Nfts": {},
        }


TagKind = typing.Union[None_, Defi, Game, Nfts]
TagJSON = typing.Union[NoneJSON, DefiJSON, GameJSON, NftsJSON]


def from_decoded(obj: dict) -> TagKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "None" in obj:
        return None_()
    if "Defi" in obj:
        return Defi()
    if "Game" in obj:
        return Game()
    if "Nfts" in obj:
        return Nfts()
    raise ValueError("Invalid enum object")


def from_json(obj: TagJSON) -> TagKind:
    if obj["kind"] == "None":
        return None_()
    if obj["kind"] == "Defi":
        return Defi()
    if obj["kind"] == "Game":
        return Game()
    if obj["kind"] == "Nfts":
        return Nfts()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "None" / borsh.CStruct(),
    "Defi" / borsh.CStruct(),
    "Game" / borsh.CStruct(),
    "Nfts" / borsh.CStruct(),
)
