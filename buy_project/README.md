# Flask template

This is a template for the Flask microservices

### Built With

* Python
* PostgreSQL
* Poetry

### Prerequisites

1. Python 3.11 - https://www.python.org/downloads/
2. Poetry 1.4.0 - https://python-poetry.org/docs/#installation

### Installation

Follow these steps to install and set up this flask template.

1. Ensure PostgreSQL server is running

2. Create a virtual environment
``` 
poetry shell
```
3. Install dependencies
``` 
poetry install
```
4. Run the app
``` 
python3 app.py
```

### Test
To test, go to localhost:5000/project, which will return a list of projects that is currently in the PostgreSQL database. To try out the other functions, use Postman to send requests to the endpoints.
