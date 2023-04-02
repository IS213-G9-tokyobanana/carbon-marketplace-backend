from enum import StrEnum

class MessageType(StrEnum):
    # Consuming
    MILESTONE_ADD = 'milestone_add'
    PROJECT_VERIFY = 'project_verify'
    OFFSETS_RESERVE = 'offsets_reserve'
    OFFSETS_COMMIT = 'offsets_commit'
    PAYMENT_FAILED = 'payment_failed'
    MILESTONE_REWARD = 'milestone_reward'
    MILESTONE_PENALISE = 'milestone_penalise'
    TASK_ADD = 'task_add'
    TASK_UPCOMING = 'upcoming'


class TaskType(StrEnum):
    # Publishing
    MILESTONE_UPCOMING = 'milestone_upcoming'
    MILESTONE_OVERDUE = 'milestone_overdue'
    PAYMENT_OVERDUE = 'payment_overdue'

    @classmethod
    def values(cls) -> list:
        return [v.value for v in cls._value2member_map_.values()]