# Projects Microservice

Built with Python, this microservice is responsible for managing projects, project milestones and reserved offsets (for a milestone, buyer and amount)

## Built With

* Python
* PostgreSQL
* Poetry

## Prerequisites

- Python 3.9 - https://www.python.org/downloads/
- Poetry 1.4.0 - https://python-poetry.org/docs/#installation

## Initial Setup

1. Clone the repository

```bash
git clone
```

2. Copy and rename the `.env.example` file to `.env`. Please remember to update the environment variables accordingly.

```bash
cp .env.example .env
```

3. Run docker compose

```bash
docker compose up
```

4. Tear down
```bash
docker compose down -v
```

## Local Development with Postgres Standalone Container
1. Change the `.env` file `POSTGRES_HOSTNAME=localhost`

2. Start the postgres container

```bash
docker run --name test-db --rm -p 5432:5432 --mount 'type=volume,src=postgres-db,dst=/var/lib/postgresql/data' -e POSTGRES_PASSWORD=changeme -e POSTGRES_USER=changeme -e POSTGRES_DB=projects postgres
```

3. Install the poetry dependencies

```bash
poetry shell
poetry install
```

4. Run the flask app with hot reload

```bash
python app.py
```

5. Make necessary code changes & test with Postman

6. Tear Down
```
docker stop test-db
docker volume rm postgres-db
```

## Testing

You can test with postman by importing the collection from the `postman` folder.

## Built With

- [Python 3.9](https://python.org/) - Programming Language
- [Flask](https://flask.palletsprojects.com/en/2.2.x/quickstart/) - Web framework
- [Flask SQL Alchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) - ORM
- [PostgreSQL](https://www.postgresql.org/) - Database


