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

class AmqpPayloadType(StrEnum):
    #Payload 'type' field
    OFFSETS_COMMIT = "offsets_commit"
    OFFSETS_RESERVE = "offsets_reserve"
    OFFSETS_ROLLBACK = "offsets_rollback"
    PROJECT_CREATE = "project_create"
    PROJECT_VERIFY = "project_verify"
    MILESTONE_ADD = "milestone_add"
    MILESTONE_REWARD = "milestone_reward"
    MILESTONE_PENALISE = "milestone_penalise"
