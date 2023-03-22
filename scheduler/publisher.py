from config import (
    RMQHOSTNAME,
    RMQPORT,
    RMQUSERNAME,
    RMQPASSWORD,
    SCHEDULER_EXCHANGE_NAME,
    PUBLISHED_TASK_EXECUTE_ROUTING_KEY,
)


# Function that republishes tasks that failed
def publishTask():
    pass


if __name__ == "__main__":
    # Need to have 3 options that can be passed in
    # 1. Upcoming Milestone
    # 2. Overdue Milestone
    # 3. Reserve Offset
    pass