# Hashbreaker

Hashbreaker is a distributed system designed to crack hashes using a master-worker architecture.

It leverages containerization to manage its various components efficiently.

## Services

The system consists of the following services:

*   **Master**: The central control unit of the application. It exposes an API (on port 8000) to accept tasks and manages the distribution of work.
*   **Minion**: The worker service responsible for processing the heavy lifting. There are 3 replicas of the minion service running to parallelize the workload.
*   **PostgreSQL**: The primary relational database used to store persistent data.
*   **PgAdmin**: A web-based administration interface for PostgreSQL, accessible on port 5050.
*   **RabbitMQ**: A message broker that facilitates asynchronous communication between the Master and Minion services. It includes a management UI on port 15672.
*   **Redis**: An in-memory data structure store used for caching and fast data access.
*   **Redis UI (Redis Commander)**: A web interface to view and manage Redis data, accessible on port 8081.

## Dependencies

To run this project, you need to have the following installed on your machine:

*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/)

## How to Run

1.  Clone the repository.
2.  Navigate to the project root directory.
3.  Run the following command to build and start all services:

    ```bash
    docker-compose up --build
    ```

Once the services are up and running, you can access the following interfaces:

*   **Master API**: `http://localhost:8000`
*   **RabbitMQ Management**: `http://localhost:15672` (User: `guest`, Pass: `guest`)
*   **PgAdmin**: `http://localhost:5050` (Email: `admin@hashbreaker.com`, Pass: `admin`)
*   **Redis Commander**: `http://localhost:8081`
