import os
from dotenv import load_dotenv

env = "production"
TOPIC_EXCHANGE_NAME = "topic_exchange"
# Binding Keys that scheduler has to listen to
BINDING_KEYS = {
    "search.milestone.add":"events.projects.*.milestone.add",
    "search.project.verify":"events.projects.*.project.verify",
    "search.offsets.reserve":"events.projects.*.offsets.reserve",
    "search.offsets.rollback":"events.projects.*.offsets.rollback",
}


if env == "production":
    load_dotenv()
    RMQHOSTNAME = os.getenv('rmqhostname')
    RMQUSERNAME = os.getenv('rmqusername')
    RMQPASSWORD = os.getenv('rmqpassword')
    RMQPORT = os.getenv('rmqport')
else:
    RMQHOSTNAME = "host.docker.internal"
    RMQUSERNAME = "guest"
    RMQPASSWORD = "guest"
    RMQPORT = 5672
    