from os import getenv
from dotenv import load_dotenv
load_dotenv()
RABBITMQ_HOSTNAME = getenv("RABBITMQ_HOSTNAME") or "13.229.231.31"
RABBITMQ_PORT = getenv("RABBITMQ_PORT") or 5672
RABBITMQ_USERNAME = getenv("RABBITMQ_USERNAME") or "guest"
RABBITMQ_PASSWORD = getenv("RABBITMQ_PASSWORD") or "guest"
EXCHANGE = getenv("EXCHANGE")
EXCHANGE_TYPE = getenv("EXCHANGE_TYPE")
MS_BASE_URL = getenv("MS_BASE_URL")
SENDGRID_API_KEY=getenv("SENDGRID_API_KEY")


