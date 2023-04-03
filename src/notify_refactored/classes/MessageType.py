from enum import StrEnum

class MessageType(StrEnum):
    PROJECT_CREATE = "project_create"
    PROJECT_VERIFY = "project_verify"
    MILESTONE_ADD = "milestone_add"
    MILESTONE_REWARD = "milestone_reward"
    MILESTONE_PENALISE = "milestone_penalise"
    MILESTONE_UPCOMING = "milestone.upcoming"
    
    PAYMENT_SUCCESS = "payment.success"
    PAYMENT_FAILED = "payment.failed"