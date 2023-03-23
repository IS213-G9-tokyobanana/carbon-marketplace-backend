import os
from dotenv import load_dotenv

load_dotenv()
RMQHOSTNAME = os.getenv('rmqhostname')
RMQUSERNAME = os.getenv('rmqusername')
RMQPASSWORD = os.getenv('rmqpassword')
RMQPORT = os.getenv('rmqport')
EXCHANGE_NAME = "topic_exchange"
TASK_EXECUTE_BINDING_KEY="events.*.*.task.execute"
POLICE_NOTIFY_ROUTING_KEY="events.police.notify.milestone.upcoming"
QUEUE_NAME="task_triggered_topic_queue"


