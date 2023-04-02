import os
from dotenv import load_dotenv

load_dotenv()
RMQHOSTNAME = os.getenv("rmqhostname")
RMQUSERNAME = os.getenv("rmqusername")
RMQPASSWORD = os.getenv("rmqpassword")
RMQPORT = os.getenv("rmqport")
PAYMENT_MS_URL = os.getenv("paymentms")
PROJECT_MS_URL = os.getenv("projectms")
USER_MS_URL = os.getenv("userms")
TEMPORAL_SERVICE_URL = os.getenv("temporalservice")
EXCHANGE_NAME = "topic_exchange"
TASK_EXECUTE_BINDING_KEY = "events.*.*.task.execute"
POLICE_NOTIFY_ROUTING_KEY = "events.police.notify.milestone.upcoming"
QUEUE_NAME = "task_execute"
POLICE_SCHEDULER_MANAGER_ROUTING_KEY = "events.police.public.task.status"
PROJECT_STATUS_URL = (
    PROJECT_MS_URL + "/project/{project_id}/milestone/{milestone_id}/status"
)
PROJECT_OFFSET_URL = (
    PROJECT_MS_URL + "/project/{project_id}/milestone/{milestone_id}/offset"
)
