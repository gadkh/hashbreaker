import sys
import time
import pika
from minion.worker.queue_sub import start_worker

def main():
    max_retries = 5
    retry_delay = 5

    while max_retries > 0:
        try:
            start_worker()
            break
        except pika.exceptions.AMQPConnectionError:
            max_retries -= 1
            time.sleep(retry_delay)
        except KeyboardInterrupt:
            break
        except Exception as e:
            sys.exit(1)
    if max_retries == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()