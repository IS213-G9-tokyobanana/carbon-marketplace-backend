from enum import StrEnum

class ProjectStatus(StrEnum):
    VERIFIED = "verified"
    PENDING = "pending"

    @classmethod
    def values(cls) -> list:
        return [v.value for v in cls._value2member_map_.values()]

class MilestoneStatus(StrEnum):
    PENDING = "pending"
    MET = "met"
    REJECTED = "rejected"

    @classmethod
    def values(cls) -> list:
        return [v.value for v in cls._value2member_map_.values()]

