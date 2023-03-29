import os
from dotenv import load_dotenv

env = "production"
TOPIC_EXCHANGE_NAME = "topic_exchange"
# Binding Keys that scheduler has to listen to
BINDING_KEYS = {
    "scheduler.milestone.add":"events.projects.*.milestone.add",
    "scheduler.project.verify":"events.projects.*.project.verify",
    "scheduler.task.add":"events.*.scheduler.task.add",
    "scheduler.offsets.reserve":"events.projects.*.offsets.reserve",
    "scheduler.offsets.commit":"events.projects.*.offsets.commit",
    "scheduler.ratings.reward":"events.projects.*.ratings.reward",
    "scheduler.ratings.penalise":"events.projects.*.ratings.penalise",
    "scheduler.payment.fail":"events.buyprojects.*.payment.failed",
}
# Routing Keys that scheduler has to publish to
PUBLISHED_TASK_EXECUTE_ROUTING_KEY = "events.scheduler.public.task.execute"

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
    