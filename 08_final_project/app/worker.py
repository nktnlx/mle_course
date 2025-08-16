import pika
import json
import sys
import datetime
from database.database import get_session
from models.ml_task import MlTask
from models.ml_model import MlModel
from routes.transaction import get_current_user
from pathlib import Path
import os
from dotenv import load_dotenv
import logging


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / 'catboost_model.cbm'

ML_QUEUE_NAME = os.getenv('ML_QUEUE_NAME', 'ml_tasks')
WORKER_NAME = os.getenv('WORKER_NAME', 'worker')

def create_rabbitmq_connection(queue_name):
    # RabbitMQ connection parameters
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

    connection_parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        heartbeat=30,
        blocked_connection_timeout=2,
        credentials=credentials
    )

    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    return connection, channel


def callback(ch, method, properties, body):
    try:
        task_data = json.loads(body)
        task_id = task_data['task_id']
        email = task_data['email']
        model_name = task_data['model_name']
        input_data = task_data['data']
        timestamp = task_data['timestamp']
        print(f'[x] Received task_id {task_id} at {timestamp} for user {email} with data: {input_data}.')

        session = next(get_session())

        try:
            user = get_current_user(email, session)
            if model_name == 'catboost':
                ml_model = MlModel(str(MODEL_PATH))
            else:
                raise Exception(f'Unsupported model: {model_name}.')

            task = MlTask(user, ml_model, session)
            result = task.execute(input_data, task_id)
            current_time = datetime.datetime.now().isoformat()
            print(f'[x] Processed task_id {task_id} at {current_time} for user {email}. {result}.')
        except Exception as inner_ex:
            print(f'[!] Error processing task for user {email}: {inner_ex}.')
        finally:
            session.close()

    except Exception as e:
        print(f'[!] Error in callback: {e}.')
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    logger.info(f'[{WORKER_NAME}] Starting ML worker')
    logger.info(f'[{WORKER_NAME}] Using model at {MODEL_PATH}')

    try:
        connection, channel = create_rabbitmq_connection(ML_QUEUE_NAME)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=ML_QUEUE_NAME, on_message_callback=callback)
        print('[*] Waiting for ML tasks. To exit press CTRL+C')
        channel.start_consuming()
    except KeyboardInterrupt:
        print('Interrupted.')
        try:
            sys.exit(0)
        except SystemExit:
            pass


if __name__ == '__main__':
    main()
