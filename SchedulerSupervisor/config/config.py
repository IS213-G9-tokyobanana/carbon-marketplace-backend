import os
from dotenv import load_dotenv

load_dotenv()
RMQHOSTNAME = os.getenv('rmqhostname')
RMQUSERNAME = os.getenv('rmqusername')
RMQPASSWORD = os.getenv('rmqpassword')
RMQPORT = os.getenv('rmqport')
EXCHANGE_NAME = "topic_exchange"
QUEUE_NAME = "task_status"
TASK_STATUS_BINDING_KEY="events.*.*.task.status"
SCHEDULER_SUPERVISOR_SCHEDULER_ROUTING_KEY="events.schedulesupervisor.scheduler.task.add"
