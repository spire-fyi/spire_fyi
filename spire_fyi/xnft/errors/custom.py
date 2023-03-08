import typing
from anchorpy.error import ProgramError


class CannotReviewOwned(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6000,
            "You cannot create a review for an xNFT that you currently own or published",
        )

    code = 6000
    name = "CannotReviewOwned"
    msg = "You cannot create a review for an xNFT that you currently own or published"


class CuratorAlreadySet(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "There is already a verified curator assigned")

    code = 6001
    name = "CuratorAlreadySet"
    msg = "There is already a verified curator assigned"


class CuratorAuthorityMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(6002, "The expected curator authority did not match expected")

    code = 6002
    name = "CuratorAuthorityMismatch"
    msg = "The expected curator authority did not match expected"


class CuratorMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6003, "The provided curator account did not match the one assigned"
        )

    code = 6003
    name = "CuratorMismatch"
    msg = "The provided curator account did not match the one assigned"


class InstallAuthorityMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(6004, "The provided xNFT install authority did not match")

    code = 6004
    name = "InstallAuthorityMismatch"
    msg = "The provided xNFT install authority did not match"


class InstallExceedsSupply(ProgramError):
    def __init__(self) -> None:
        super().__init__(6005, "The max supply has been reached for the xNFT")

    code = 6005
    name = "InstallExceedsSupply"
    msg = "The max supply has been reached for the xNFT"


class InstallOwnerMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6006,
            "The asserted authority/owner did not match that of the Install account",
        )

    code = 6006
    name = "InstallOwnerMismatch"
    msg = "The asserted authority/owner did not match that of the Install account"


class MetadataIsImmutable(ProgramError):
    def __init__(self) -> None:
        super().__init__(6007, "The metadata of the xNFT is marked as immutable")

    code = 6007
    name = "MetadataIsImmutable"
    msg = "The metadata of the xNFT is marked as immutable"


class MustBeApp(ProgramError):
    def __init__(self) -> None:
        super().__init__(6008, "The xNFT must be of `Kind::App` for this operation")

    code = 6008
    name = "MustBeApp"
    msg = "The xNFT must be of `Kind::App` for this operation"


class RatingOutOfBounds(ProgramError):
    def __init__(self) -> None:
        super().__init__(6009, "The rating for a review must be between 0 and 5")

    code = 6009
    name = "RatingOutOfBounds"
    msg = "The rating for a review must be between 0 and 5"


class ReviewInstallMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6010, "The installation provided for the review does not match the xNFT"
        )

    code = 6010
    name = "ReviewInstallMismatch"
    msg = "The installation provided for the review does not match the xNFT"


class SupplyReduction(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6011, "Updated supply is less than the original supply set on creation"
        )

    code = 6011
    name = "SupplyReduction"
    msg = "Updated supply is less than the original supply set on creation"


class SuspendedInstallation(ProgramError):
    def __init__(self) -> None:
        super().__init__(6012, "Attempting to install a currently suspended xNFT")

    code = 6012
    name = "SuspendedInstallation"
    msg = "Attempting to install a currently suspended xNFT"


class UnauthorizedInstall(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6013, "The access account provided is not associated with the wallet"
        )

    code = 6013
    name = "UnauthorizedInstall"
    msg = "The access account provided is not associated with the wallet"


class UpdateAuthorityMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6014,
            "The signer did not match the update authority of the metadata account or the owner",
        )

    code = 6014
    name = "UpdateAuthorityMismatch"
    msg = "The signer did not match the update authority of the metadata account or the owner"


class UpdateReviewAuthorityMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6015,
            "The signing authority for the xNFT update did not match the review authority",
        )

    code = 6015
    name = "UpdateReviewAuthorityMismatch"
    msg = "The signing authority for the xNFT update did not match the review authority"


class UriExceedsMaxLength(ProgramError):
    def __init__(self) -> None:
        super().__init__(6016, "The metadata URI provided exceeds the maximum length")

    code = 6016
    name = "UriExceedsMaxLength"
    msg = "The metadata URI provided exceeds the maximum length"


CustomError = typing.Union[
    CannotReviewOwned,
    CuratorAlreadySet,
    CuratorAuthorityMismatch,
    CuratorMismatch,
    InstallAuthorityMismatch,
    InstallExceedsSupply,
    InstallOwnerMismatch,
    MetadataIsImmutable,
    MustBeApp,
    RatingOutOfBounds,
    ReviewInstallMismatch,
    SupplyReduction,
    SuspendedInstallation,
    UnauthorizedInstall,
    UpdateAuthorityMismatch,
    UpdateReviewAuthorityMismatch,
    UriExceedsMaxLength,
]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: CannotReviewOwned(),
    6001: CuratorAlreadySet(),
    6002: CuratorAuthorityMismatch(),
    6003: CuratorMismatch(),
    6004: InstallAuthorityMismatch(),
    6005: InstallExceedsSupply(),
    6006: InstallOwnerMismatch(),
    6007: MetadataIsImmutable(),
    6008: MustBeApp(),
    6009: RatingOutOfBounds(),
    6010: ReviewInstallMismatch(),
    6011: SupplyReduction(),
    6012: SuspendedInstallation(),
    6013: UnauthorizedInstall(),
    6014: UpdateAuthorityMismatch(),
    6015: UpdateReviewAuthorityMismatch(),
    6016: UriExceedsMaxLength(),
}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
