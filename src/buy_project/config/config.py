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
PAYMENT_STATUS_ROUTING_KEY = "events.buyprojects.public.payment.{payment_status}"
