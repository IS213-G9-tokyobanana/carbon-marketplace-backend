# Project Polica complex microservice

This is the Project Police complex microservice. It is a Flask microservice that uses RabbitMQ as the message broker.

### Built With

- Python
- Poetry

### Prerequisites

1. Python 3.11 - https://www.python.org/downloads/
2. Poetry 1.4.0 - https://python-poetry.org/docs/#installation

### Installation

Follow these steps to install and set up this flask template.

1. Ensure docker server is running

2. Build the docker container image

```
docker build -t projectpolice .
```

3. Run the docker container

```
docker run -d -p 5000:5000 projectpolice
```

4. Create a virtual environment

```
poetry shell
```

5. Install dependencies

```
poetry install
```

6. Run the app

```
python3 app.py
```
