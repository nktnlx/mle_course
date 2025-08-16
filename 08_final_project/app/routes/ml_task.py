from fastapi import APIRouter, Depends, HTTPException, status
from database.database import get_session
from services.crud.transaction import get_transaction_by_transaction_id
from routes.transaction import get_current_user
from models.ml_model import MlModel
from pydantic import BaseModel, confloat, conint
import pika
import json
import uuid
import datetime
from typing import Optional, Literal
import os


prediction_route = APIRouter(tags=['Prediction'])

model = MlModel('catboost_model.cbm')
loaded_model = {'catboost': model}

class ModelFeatures(BaseModel):
    HadAngina: conint(ge=0, le=1)
    ChestScan: conint(ge=0, le=1)
    GeneralHealth: conint(ge=1, le=5)
    AgeCategory: Literal[
        'Age_18_to_24', 'Age_25_to_29', 'Age_30_to_34', 'Age_35_to_39',
        'Age_40_to_44', 'Age_45_to_49', 'Age_50_to_54', 'Age_55_to_59',
        'Age_60_to_64', 'Age_65_to_69', 'Age_70_to_74', 'Age_75_to_79',
        'Age_80_or_older'
    ]
    DifficultyWalking: conint(ge=0, le=1)
    RemovedTeeth: conint(ge=0, le=1)
    HadDiabetes: conint(ge=0, le=1)
    SleepHours: confloat(ge=3, le=11)
    IsMale: conint(ge=0, le=1)
    WeightInKilograms: confloat(ge=45, le=150)
    SmokerStatus: Literal[
        'Former smoker', 'Never smoked', 'Smokes_every_day', 'Smokes_some_days'
    ]
    HeightInMeters: confloat(ge=1.5, le=1.95)
    AlcoholDrinkers: conint(ge=0, le=1)
    LastCheckupTime: Literal[
        '5_or_more_years_ago', 'Past_2_years', 'Past_5_years', 'Past_year'
    ]
    PhysicalHealthDays: confloat(ge=0, le=30)


class UserInput(BaseModel):
    email: str
    data: ModelFeatures
    model_name: Optional[str] = 'catboost'


@prediction_route.post('/prediction')
async def make_prediction(data: UserInput, session=Depends(get_session)) -> dict:
    input_data = [data.data.HadAngina, data.data.ChestScan, data.data.GeneralHealth,
                  data.data.AgeCategory, data.data.DifficultyWalking, data.data.RemovedTeeth,
                  data.data.HadDiabetes, data.data.SleepHours, data.data.IsMale,
                  data.data.WeightInKilograms, data.data.SmokerStatus, data.data.HeightInMeters,
                  data.data.AlcoholDrinkers, data.data.LastCheckupTime, data.data.PhysicalHealthDays]
    current_user = get_current_user(data.email, session)

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
        'email': current_user.email
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
