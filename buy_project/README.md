# Project Polica complex microservice

The Buy Project complex microservice (ms) is a service that enables buyers to purchase a green project using our platform.

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
temporal_payment_failed_worker   | Starting payment failed worker
temporal_payment_success_worker  | Starting payment success worker
temporal_start_payment_worker    | Starting start payment worker
buy_projects                     |  * Serving Flask app 'app'
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

1. Web UI sends a POST request to Buy Project to start a payment process. 
2. Payment is successful. Web UI sends a POST request to Stripe. Stripe post payment success to Buy Project.
3. Payment fails. Web UI sends a POST request to Stripe. Stripe post payment failed to Buy Project.

Based on the scenario, the following functionailities should be tested:

Scenario 1 - To start a payment process, the functions below are executed in the `start_payment` workflow:
1. POST request to Payments ms to create a payment intent.
2. Once the step above is executed and payment intent id is obtained, send a POST request to Projetcs ms to reserve offset.

Scenario 2 - `payment_success_workflow` when payment is successful:
1. GET request to Payments ms to get payment details based on the payment intent id
2. PATCH request to Projects ms to commit deduct offset
3. POST request to Users ms to create an offset for users
4. Publish message to Notifier through RabbitMQ to indicate payment success

Scenario 3 - `payment_failed_workflow` when the payment fails:
1. GET request to Payments ms to get payment details based on the payment intent id
2. DELETE request to Projects ms to remove reserved offset
3. Publish message to Notifier through RabbitMQ to indicate payment fails.