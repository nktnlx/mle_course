from fastapi import APIRouter, Depends, HTTPException, status
from database.database import get_session
from routes.balance import get_current_user
from services.crud.transaction import get_transaction_by_transaction_id
from models.ml_model import MlModel
from pydantic import BaseModel, confloat, conint
import pika
import json
import uuid
import datetime
from typing import Optional
import os


prediction_route = APIRouter(tags=['Prediction'])

model = MlModel('catboost_model.cbm', prediction_cost=5.55)
loaded_model = {'catboost': model}

class ModelFeatures(BaseModel):
    sex: str
    age: conint(ge=0)
    is_alone: str
    pclass: str
    fare: confloat(ge=0)


class UserInput(BaseModel):
    email: str
    data: ModelFeatures
    model_name: Optional[str] = 'catboost'


@prediction_route.post('/prediction')
async def make_prediction(data: UserInput, session=Depends(get_session)) -> dict:
    input_data = [data.data.sex, data.data.age, data.data.is_alone, data.data.pclass, data.data.fare]
    current_user = get_current_user(data.email, session)
    model_to_use = loaded_model[data.model_name]

    if current_user.balance.amount < model_to_use.prediction_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Not enough balance to make a prediction.'
        )

    task_id = str(uuid.uuid4())
    current_time = datetime.datetime.now().isoformat()
    task_data = {
        'task_id': task_id,
        'email': data.email,
        'model_name': data.model_name,
        'data': input_data,
        'timestamp': current_time
    }

    try:
        # Get RabbitMQ connection parameters from environment variables
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
        rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
        rabbitmq_pass = os.getenv("RABBITMQ_PASS", "guest")

        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        connection_parameters = pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port,
            credentials=credentials,
            heartbeat=30,
            blocked_connection_timeout=2
        )
        connection = pika.BlockingConnection(connection_parameters)
        channel = connection.channel()
        channel.queue_declare(queue='ml_tasks', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='ml_tasks',
            body=json.dumps(task_data),
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )
        connection.close()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error publishing task: {e}.'
        )

    return {
        'message': 'ML task was queued for execution. Results will appear soon.',
        'task_id': task_id,
        'user_id': current_user.user_id,
        'email': current_user.email,
        'balance_before_prediction': current_user.balance.amount
    }


@prediction_route.get('/result')
async def get_result_by_task_id(task_id: str, session=Depends(get_session)) -> dict:
    current_transaction = get_transaction_by_transaction_id(task_id, session)
    if not current_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Transaction not found for task_id: {task_id}.'
        )
    return {
        'prediction_result': current_transaction[0].prediction_result
    }
