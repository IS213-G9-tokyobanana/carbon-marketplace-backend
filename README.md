<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/IS213-G9-tokyobanana/carbon-marketplace-backend">
    <img src=".github/assets/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Carbon Offset Marketplace</h3>

  <p align="center">
    A place for people to buy carbon offsets to help reduce their carbon footprint and support green projects.
    <br />
    <a href="https://github.com/IS213-G9-tokyobanana/carbon-marketplace-backend"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/IS213-G9-tokyobanana/carbon-marketplace-backend">View Demo</a>
    ·
    <a href="https://github.com/IS213-G9-tokyobanana/carbon-marketplace-backend/issues/new?assignees=&labels=bug&template=bug-report.md&title=%5BMICROSERVICE_NAME%5D%3A+ISSUE_TITLE">Report Bug</a>
    ·
    <a href="https://github.com/IS213-G9-tokyobanana/carbon-marketplace-backend/issues/new?assignees=&labels=enhancement&template=feature-request.md&title=%5BMICROSERVICE_NAME%5D%3A+FEATURE_TITLE">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details open>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#initial-setup">Initial Setup</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#local-development">Local Development</a></li>
      </ul>
    </li>
    <li>
      <a href="#usage">Usage</a>
      <ul>
        <li><a href="#api-documentation">API Documentation</a></li>
      </ul>
    </li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com) -->

Our app is a platform for companies any entity to (1) obtain funding for new green projects and (2) further monetise existing green projects that have already began consistently removing CO2 from environment.

The focus is primarily on the voluntary market where anyone can fund new projects or support existing projects by buying carbon credits sold by these companies.

We are not focusing on compliance market to facilitate the trading of carbon credits b/w companies who have hit their carbon credit cap set by govt and want to buy carbon credits from other companies with surplus carbon credits (companies whose carbon credits are below the cap set by govt).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- [Docker](https://www.docker.com/) (Container Runtime)
- [Temporal](https://temporal.io/) (Workflow Engine)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/) (Python Web Framework)
- [Express.js](https://expressjs.com/) (Node.js Web Framework)
- [PostgreSQL](https://www.postgresql.org/) (SQL Database)
- [MongoDB](https://www.mongodb.com/) (NoSQL Database)
- [RabbitMQ](https://www.rabbitmq.com/) (Message Broker)
- [MeiliSearch](https://www.meilisearch.com/) (Search Engine)
- [Terrafom](https://www.terraform.io/) (Infrastructure as Code)
- [Prometheus](https://prometheus.io/) (Monitoring)
- [Grafana](https://grafana.com/) (Monitoring)
- [Istio](https://istio.io/) (API Gateway / Service Mesh)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Initial Setup

To get a local copy of all the microservices up and running follow these steps.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Optional] [Make](https://www.gnu.org/software/make/)
- [Deployment only] [Terraform](https://www.terraform.io/downloads.html)
- [Deployment only] [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)

### Local development

1. Clone the repo
   ```bash
   git clone https://github.com/IS213-G9-tokyobanana/carbon-marketplace-backend.git
   ```
2. Initialize repo with .env file

   ```bash
   # If you have make installed
   make init
   ```

   <ins><em>OR</em></ins>

   ```bash
   cp ./deployment/.docker/.env.example .env
   ```

3. Start the services

   ```bash
   # If you have make installed
   make dev
   ```

   <ins><em>OR</em></ins>

   ```bash
   docker-compose -f ./docker-compose.yaml up --build --remove-orphans --force-recreate -d
   ```

4. To stop the services, run

   ```bash
   # If you have make installed
   make stop
   ```

   <ins><em>OR</em></ins>

   ```bash
   docker-compose -f ./docker-compose.yaml --env-file .env down
   ```

5. To prune the services, run

   ```bash
   # If you have make installed
   make prune-all
   ```

   <ins><em>OR</em></ins>

   ```bash
   docker system prune -a --volumes
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

### API Documentations

API documentation can be found [here](https://example.com).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Acknowledgments

- []()
- []()
- []()

<p align="right">(<a href="#readme-top">back to top</a>)</p>
