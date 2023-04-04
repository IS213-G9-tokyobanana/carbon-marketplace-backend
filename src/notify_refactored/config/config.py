from os import getenv
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_HOSTNAME = getenv("RABBITMQ_HOSTNAME")
RABBITMQ_PORT = getenv("RABBITMQ_PORT")
RABBITMQ_USERNAME = getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = getenv("RABBITMQ_PASSWORD")
EXCHANGE = getenv("EXCHANGE")
EXCHANGE_TYPE = getenv("EXCHANGE_TYPE")
USERS_BASE_URL = getenv("USERS_BASE_URL")
VERIFIERS_EMAILS = getenv("VERIFIERS_EMAILS")
SENDGRID_API_KEY=getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL=getenv("SENDGRID_FROM_EMAIL")
