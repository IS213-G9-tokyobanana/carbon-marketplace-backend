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

3. Run docker compose

```bash
docker compose up
```

5. Test with Postman by importing the collection from the `postman` folder. Expected results are in the `examples` under each request in the postman collection.

6. Tear down
```bash
docker compose down
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



