# HashBreaker Minion Node

The **Minion Node** is the worker component of the HashBreaker distributed MD5 hash cracking system. It is responsible for performing the actual computational work of brute-forcing hash chunks.

## Key Responsibilities

*   **Task Consumption**: Listens to the job queue (RabbitMQ) for new cracking tasks dispatched by the Master.
*   **Brute-Force Cracking**: Processes assigned chunks of the search space, attempting to find a plaintext string that matches the target MD5 hash.
*   **Result Reporting**:
    *   If a match is found, it publishes the result to the results queue.
    *   If no match is found in the assigned chunk, it decrements the pending chunk counter in Redis.
*   **Coordination**: Uses Redis to coordinate with other minions to determine if a hash has been fully exhausted without success.

## How It Works

1.  **Startup**: The Minion initializes and connects to RabbitMQ and Redis.
2.  **Listening**: It waits for `ChunkTask` messages on the configured jobs queue.
3.  **Processing**: Upon receiving a task, it calculates MD5 hashes for the specified range of candidates (defined by a prefix and a range).
4.  **Success**: If the calculated hash matches the target, it immediately sends a `CrackResult` with the password to the results queue.
5.  **Failure/Coordination**: If the chunk is exhausted without a match, it updates a shared counter in Redis. If it detects it processed the last chunk and no password was found, it reports a "Not Found" status.

## Tech Stack

*   **Language**: Python
*   **Messaging**: RabbitMQ (Pika)
*   **Coordination**: Redis
*   **Hashing**: Python `hashlib` (MD5)
