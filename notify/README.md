# Notify Microservice

Built with python, this microservice is responsible for listening on queues and notifying respective buyer,seller and verifiers on updates made to a project

## Prerequisites

1. Python 3.11 - https://www.python.org/downloads/release/python-3110/
2. Poetry 1.4.0 - https://python-poetry.org/docs/#installation
3. Docker 20.10.8 - https://docs.docker.com/get-docker/
4. Have a live RabbitMQ instance running. Environment file should be configured to attach to the RabbitMQ instance.

## Initial Setup

1. Clone the repository

```bash
git clone
```

2. Copy and rename the `.env.example` file to `.env`. Please remember to update the environment variables accordingly.

```bash
cp .env.example .env
```

3. Change `RABBITMQ_HOSTNAME=changeme` and `RABBITMQ_PORT=changeme` in the `.env` file to the ip address and port number provisioned for the rabbitmq server. 

```bash
RABBITMQ_HOSTNAME=changeme
RABBITMQ_PORT=changeme
```

4. Change `RABBITMQ_USERNAME=changeme` and `RABBITMQ_PASSWORD=changeme` to the `guest`

```bash
RABBITMQ_USERNAME=changeme
RABBITMQ_PASSWORD=changeme
```
5. Add in the `SENDGRID_API_KEY` 

5. Run docker compose 

```bash 
docker build -t notify .
```

### Local Development

For local development, configure the rabbitMQ hostname variables in the `.env` file to 'localhost'. Then, continue with the following steps after running the docker container.

1. Create a virtual environment

```
poetry shell
```

2. Install dependencies

```
poetry install
```

3. Run the app

```
python3 notify.py
```