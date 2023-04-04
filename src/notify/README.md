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

```
3. Add in the `SENDGRID_API_KEY` and `SENDGRID_FROM_EMAIL` in the `.env` file

4. Start up the users microservice with `docker compose up` in the `users` folder. Create 1 buyer, 1 seller and 1 verifier with valid emails to see the email sent to the respective emails.

5. `docker compose up` 
```bash 
docker build -t notify .
```

### Testing
Refer to `Notify MS` in Notion for the payload to be sent to which queue and the expected result.


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