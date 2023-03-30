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
    OFFSETS_COMMIT = "offsets.commit"
    OFFSETS_RESERVE = "offsets.reserve"
    OFFSETS_ROLLBACK = "offsets.rollback"
    PROJECT_CREATE = "project.create"
    PROJECT_VERIFY = "project.verify"
    MILESTONE_ADD = "milestone.add"
    MILESTONE_REWARD = "milestone.reward"
    MILESTONE_PENALISE = "milestone.penalise"
