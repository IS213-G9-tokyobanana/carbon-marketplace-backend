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
POLICE_NOTIFY_UPCOMING_ROUTING_KEY = "events.police.notify.milestone.upcoming"
POLICE_NOTIFY_REWARD_ROUTING_KEY = "events.projects.notify.ratings.reward"
POLICE_NOTIFY_PENALISE_ROUTING_KEY = "events.projects.notify.ratings.penalise"
POLICE_NOTIFY_ROLLBACK_ROUTING_KEY = "events.projects.notify.payment.failed"
QUEUE_NAME = "task_execute"
POLICE_SCHEDULER_MANAGER_ROUTING_KEY = "events.police.public.task.status"
