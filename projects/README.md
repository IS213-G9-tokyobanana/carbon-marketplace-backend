# Projects Microservice

Built with Python, this microservice is responsible for managing projects, project milestones and reserved offsets (for a milestone, buyer and amount)

## Prerequisites

- Python 3.11 - https://www.python.org/downloads/release/python-3110/
- Poetry 1.4.0 - https://python-poetry.org/docs/#installation

## Testing using `docker compose` with Provisioned RabbitMQ

1. Clone the repository

```bash
git clone
```

2. Copy and rename the `.env.example` file to `.env`.

```bash
cp .env.example .env
```

3. Change `RABBITMQ_HOSTNAME=changeme` in the `.env` file to the ip address provisioned for the rabbitmq server.

```bash
RABBITMQ_HOSTNAME=changeme  # `localhost` for local development with `docker-compose.dev.yml`; `rabbitmq3` for testing with `docker-compose.rmq.yml`; <ipaddress for provisioned rabbitmq> for integration

```

4. Run docker compose

```bash
docker compose up
```

5. Test with Postman by importing the collection from the `postman` folder.

6. Tear down
```bash
docker compose down
```

## Testing using `docker compose` with Local RabbitMQ
1. Change `RABBITMQ_HOSTNAME=changeme` in the `.env` file to `RABBITMQ_HOSTNAME=rabbitmq3`

```bash
RABBITMQ_HOSTNAME=rabbitmq3  # `localhost` for local development with `docker-compose.dev.yml`; `rabbitmq3` for testing with `docker-compose.rmq.yml`; <ipaddress for provisioned rabbitmq> for integration

```

2. Build docker compose for `docker-compose.rmq.yml`

```bash
docker compose -f docker-compose.rmq.yml up
```

3. Tear down
```bash
docker compose -f docker-compose.rmq.yml down
```

## Local Development with RabbitMQ and PostgreSQL
1. Update `.env` file
```bash
POSTGRES_HOSTNAME=localhost # localhost for local development with `docker-compose.dev.yml`; db for testing with `docker-compose.rmq.yml`, `docker-compose.yml`
RABBITMQ_HOSTNAME=localhost # `localhost` for local development with `docker-compose.dev.yml`; `rabbitmq3` for testing with `docker-compose.rmq.yml`; <ipaddress for provisioned rabbitmq> for integration
```

2. Run RabbitMQ and PostgreSQL with docker compose
```bash
docker compose -f docker-compose.dev.yml up
```

3. Open another terminal and install the poetry dependencies
```bash
poetry shell
poetry install
```

4. Run the flask app with hot reload

```bash
python app.py
```

5. Make necessary code changes & test with Postman

6. Exit the poetry shell
```bash
exit
```

7. Tear Down of RabbitMQ and PostgreSQL
```bash
docker compose -f docker-compose.dev.yml down
```

## Testing

You can test with postman by importing the collection from the `postman` folder.

## Built With

- [Python 3.11](https://www.python.org/downloads/release/python-3110/) - Programming Language
- [Flask](https://flask.palletsprojects.com/en/2.2.x/quickstart/) - Web framework
- [Flask SQL Alchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) - ORM
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Poetry](https://python-poetry.org/docs/basic-usage/) - Dependency Management
- [Docker](https://docs.docker.com/engine/reference/commandline/cli/) - Containerization
- [Docker Compose](https://docs.docker.com/engine/reference/commandline/compose/) - Container Orchestration
- [RabbitMQ](https://www.rabbitmq.com/tutorials/tutorial-three-python.html) - Message Broker



