# Project Polica complex microservice

This is the Project Police complex microservice. It is a Flask microservice that uses RabbitMQ as the message broker.

### Built With

- Python
- Poetry

### Prerequisites

1. Python 3.11 - https://www.python.org/downloads/
2. Poetry 1.4.0 - https://python-poetry.org/docs/#installation
3. Docker 20.10.8 - https://docs.docker.com/get-docker/
4. Have a live RabbitMQ instance running. Environment file should be configured to attach to the RabbitMQ instance.

### Initial Setup

1.  Clone the repository

```bash
git clone
```

2.  Copy and rename the `.env.example` file to `.env`. Please remember to update the environment variables accordingly.

```bash
cp .env.example .env
```

3.  Change configuration in `config.py` file based on whether it is production or development environment.

### Running the app

Follow these steps to set up this complex microservice.

1. Ensure docker server is running

2. Spin up the docker container

```
docker compose up
```

Once the container is set up and running, you should be able to see the following output:

```
temporal_worker  | Starting worker
amqp             | monitoring the exchange topic_exchange on binding key events.*.*.task.execute ...
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
python3 checkAmqp.py
```

### Testing

As this complex microservice heavily depends on the other microservices, the current testing that can be done is to check whether each scenario will be executed as expected based on the message received by Project Police. The following are the scenarios that can be tested:

1. Trigger message flags project milestone as upcoming. In this case, Project Police will publish a message to Notifier ms through RabbitMQ (to request verifier to verify the milestone).
2. Trigger message flags project milestone as penalise. In this case, Project Police will send a HTTP request to Project ms (to request a change in project's rating)
3. Trigger message flags reserved offset as overdue. In this case, Project Police will trigger temporal workflow to perform these functions

To test the above scenarios, publish message to exchange `topic_exchange` on queue `task_execute`.
