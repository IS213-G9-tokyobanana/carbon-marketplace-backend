# Project Polica complex microservice

This is the Schedular Supervisor complex microservice. It is a Flask microservice that uses RabbitMQ as the message broker.

### Built With

- Python 3.11
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

2. Build the docker container image

```
docker build -t supervisor .
```

3. Run the docker container

```
docker run -d supervisor
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
python3 supervisor.py
```
