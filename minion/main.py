import sys
import time
import pika
from minion.worker.queue_sub import start_worker
from shared.logger import setup_logger

logger = setup_logger(__name__)

def main():
    logger.info("Minion entry point initializing...")
    max_retries = 5
    retry_delay = 5

    while max_retries > 0:
        try:
            start_worker()
            break
        except pika.exceptions.AMQPConnectionError as e:
            max_retries -= 1
            logger.warning(f"RabbitMQ not ready yet. Retries left: {max_retries}. Waiting {retry_delay}s... ({e})")
            time.sleep(retry_delay)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Shutting down Minion gracefully.")
            break
        except Exception as e:
            logger.error(f"Unexpected fatal error in Minion loop: {e}", exc_info=True)
            sys.exit(1)
    if max_retries == 0:
        logger.error("Exhausted all 5 retries to connect to RabbitMQ. Minion container will exit.")
        sys.exit(1)


if __name__ == "__main__":
    main()