import os
from dotenv import load_dotenv

env = "production"
TOPIC_EXCHANGE_NAME = "topic_exchange"
# Binding Keys that scheduler has to listen to
BINDING_KEYS = {
    "MILESTONE_ADD":"events.projects.*.milestone.add",
    "PROJECT_VERIFY":"events.projects.*.project.verify",
    "TASK_ADD":"events.*.scheduler.task.add",
    "OFFSET_RESERVE":"events.projects.*.offsets.reserve",
    "OFFSET_COMMIT":"events.projects.*.offsets.commit",
    "RATINGS_REWARD":"events.projects.*.ratings.reward",
    "PAYMENT_FAIL":"events.buyprojects.*.payment.failed",
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
    