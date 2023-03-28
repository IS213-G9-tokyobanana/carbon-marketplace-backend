import os
from dotenv import load_dotenv

load_dotenv()
RMQHOSTNAME = os.getenv("rmqhostname")
RMQUSERNAME = os.getenv("rmqusername")
RMQPASSWORD = os.getenv("rmqpassword")
RMQPORT = os.getenv("rmqport")
EXCHANGE_NAME = "topic_exchange"
TASK_EXECUTE_BINDING_KEY = "events.*.*.task.execute"
POLICE_NOTIFY_ROUTING_KEY = "events.police.notify.milestone.upcoming"
QUEUE_NAME = "task_execute"
POLICE_SCHEDULER_MANAGER_ROUTING_KEY = "events.police.public.task.status"
PROJECT_MS_URL = os.getenv("projectms")
PROJECT_STATUS_URL = (
    PROJECT_MS_URL + "/project/{project_id}/milestone/{milestone_id}/{task}"
)
PAYMENT_MS_URL = os.getenv("paymentms")
TEMPORAL_SERVICE_URL = os.getenv("temporalservice")
