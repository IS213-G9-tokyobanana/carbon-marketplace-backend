import os
from dotenv import load_dotenv

env = "production"
TOPIC_EXCHANGE_NAME = "topic_exchange"
# Binding Keys that scheduler has to listen to
BINDING_KEYS = {
    "milestone_add":"events.projects.*.milestone.add",
    "project_verify":"events.projects.*.project.verify",
    "task_add":"events.*.scheduler.task.add",
    "offsets_reserve":"events.projects.*.offsets.reserve",
    "offsets_commit":"events.projects.*.offsets.commit",
    "ratings_reward":"events.projects.*.ratings.reward",
    "ratings_penalise":"events.projects.*.ratings.penalise",
    "payment_fail":"events.buyprojects.*.payment.failed",
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
    