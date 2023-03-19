import os
from dotenv import load_dotenv

env = "development"

if env == "production":
    load_dotenv()
    RMQHOSTNAME = os.getenv('rmqhostname')
    RMQUSERNAME = os.getenv('rmqusername')
    RMQPASSWORD = os.getenv('rmqpassword')
    RMQPORT = os.getenv('rmqport')
    TASK_EXECUTE_ROUTING_KEY="events.*.*.task.execute"
    EXCHANGE_NAME = "topic_exchange"
else:
    RMQHOSTNAME = "localhost"
    RMQUSERNAME = "guest"
    RMQPASSWORD = "guest"
    RMQPORT = 5672
    TASK_EXECUTE_ROUTING_KEY="events.*.*.task.execute"
    EXCHANGE_NAME = "topic_exchange"
