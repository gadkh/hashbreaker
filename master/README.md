# HashBreaker Master Service

The **Master Node** is the central orchestrator of the HashBreaker distributed MD5 hash cracking system. It provides a REST API for clients to interact with the system and manages the lifecycle of cracking tasks.

## Key Responsibilities

*   **Task Management**: Receives cracking requests and dispatches them to the distributed worker queue (RabbitMQ).
*   **Result Aggregation**: Consumes results from Minion nodes and updates the database with the found passwords or status updates.
*   **Persistence**: Maintains the state of all tasks in a relational database.

## How It Works

1.  **Submission**: A client submits an MD5 hash via the `POST /cracker/crack` endpoint.
2.  **Dispatch**: The Master service validates the request, creates a record in the database, and publishes the task to the message queue.
3.  **Processing**: Distributed **Minion** nodes pick up the task, attempt to crack the hash, and publish the result back to a results queue.
4.  **Completion**: The Master's background consumer (`start_results_consumer`) picks up the result and updates the task status in the database.
5.  **Status Check**: Clients can query the `GET /cracker/status/{hash_value}` endpoint to see if the hash has been cracked.

## Tech Stack

*   **Language**: Python
*   **Framework**: FastAPI
*   **Database**: SQLAlchemy (Async)
*   **Messaging**: RabbitMQ
