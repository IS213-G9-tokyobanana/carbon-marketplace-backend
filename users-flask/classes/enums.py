from enum import StrEnum


class UserRole(StrEnum):
    BUYER = "buyer"
    SELLER = "seller"
    VERIFIER = "verifier"
    @classmethod
    def values(cls) -> list:
        return [v.value for v in cls._value2member_map_.values()]


class OffsetStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REFUND = "refund"

    @classmethod
    def values(cls) -> list:
        return [v.value for v in cls._value2member_map_.values()]

