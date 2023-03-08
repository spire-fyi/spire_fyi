from __future__ import annotations
from . import creators_param, tag
import typing
from dataclasses import dataclass
from construct import Container, Construct
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class CreateXnftParamsJSON(typing.TypedDict):
    creators: list[creators_param.CreatorsParamJSON]
    curator: typing.Optional[str]
    install_authority: typing.Optional[str]
    install_price: int
    install_vault: str
    seller_fee_basis_points: int
    supply: typing.Optional[int]
    symbol: str
    tag: tag.TagJSON
    uri: str


@dataclass
class CreateXnftParams:
    layout: typing.ClassVar = borsh.CStruct(
        "creators"
        / borsh.Vec(typing.cast(Construct, creators_param.CreatorsParam.layout)),
        "curator" / borsh.Option(BorshPubkey),
        "install_authority" / borsh.Option(BorshPubkey),
        "install_price" / borsh.U64,
        "install_vault" / BorshPubkey,
        "seller_fee_basis_points" / borsh.U16,
        "supply" / borsh.Option(borsh.U64),
        "symbol" / borsh.String,
        "tag" / tag.layout,
        "uri" / borsh.String,
    )
    creators: list[creators_param.CreatorsParam]
    curator: typing.Optional[Pubkey]
    install_authority: typing.Optional[Pubkey]
    install_price: int
    install_vault: Pubkey
    seller_fee_basis_points: int
    supply: typing.Optional[int]
    symbol: str
    tag: tag.TagKind
    uri: str

    @classmethod
    def from_decoded(cls, obj: Container) -> "CreateXnftParams":
        return cls(
            creators=list(
                map(
                    lambda item: creators_param.CreatorsParam.from_decoded(item),
                    obj.creators,
                )
            ),
            curator=obj.curator,
            install_authority=obj.install_authority,
            install_price=obj.install_price,
            install_vault=obj.install_vault,
            seller_fee_basis_points=obj.seller_fee_basis_points,
            supply=obj.supply,
            symbol=obj.symbol,
            tag=tag.from_decoded(obj.tag),
            uri=obj.uri,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "creators": list(map(lambda item: item.to_encodable(), self.creators)),
            "curator": self.curator,
            "install_authority": self.install_authority,
            "install_price": self.install_price,
            "install_vault": self.install_vault,
            "seller_fee_basis_points": self.seller_fee_basis_points,
            "supply": self.supply,
            "symbol": self.symbol,
            "tag": self.tag.to_encodable(),
            "uri": self.uri,
        }

    def to_json(self) -> CreateXnftParamsJSON:
        return {
            "creators": list(map(lambda item: item.to_json(), self.creators)),
            "curator": (None if self.curator is None else str(self.curator)),
            "install_authority": (
                None if self.install_authority is None else str(self.install_authority)
            ),
            "install_price": self.install_price,
            "install_vault": str(self.install_vault),
            "seller_fee_basis_points": self.seller_fee_basis_points,
            "supply": self.supply,
            "symbol": self.symbol,
            "tag": self.tag.to_json(),
            "uri": self.uri,
        }

    @classmethod
    def from_json(cls, obj: CreateXnftParamsJSON) -> "CreateXnftParams":
        return cls(
            creators=list(
                map(
                    lambda item: creators_param.CreatorsParam.from_json(item),
                    obj["creators"],
                )
            ),
            curator=(
                None if obj["curator"] is None else Pubkey.from_string(obj["curator"])
            ),
            install_authority=(
                None
                if obj["install_authority"] is None
                else Pubkey.from_string(obj["install_authority"])
            ),
            install_price=obj["install_price"],
            install_vault=Pubkey.from_string(obj["install_vault"]),
            seller_fee_basis_points=obj["seller_fee_basis_points"],
            supply=obj["supply"],
            symbol=obj["symbol"],
            tag=tag.from_json(obj["tag"]),
            uri=obj["uri"],
        )
