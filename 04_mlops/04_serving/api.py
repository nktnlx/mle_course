import uvicorn
import joblib
import subprocess

import pandas as pd
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel


try:
    subprocess.run(['dvc', 'pull'], check=True)
except subprocess.CalledProcessError as e:
    pass


def load_model():
    try:
        with open('model.pkl', 'rb') as file:
            model = joblib.load(file)
            return model
    except FileNotFoundError:
        pass


is_ready = True
model = load_model()
app = FastAPI()


class ModelRequestData(BaseModel):
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    pH: float
    sulphates: float
    alcohol: float


class Result(BaseModel):
    predicted_quality: float


@app.get('/healthcheck')
def health(data={'fixed_acidity': 7.4,
                'volatile_acidity': 0.7,
                'citric_acid': 0.0,
                'residual_sugar': 1.9,
                'chlorides': 0.076,
                'free_sulfur_dioxide': 11.0,
                'total_sulfur_dioxide': 34.0,
                'density': 0.9978,
                'pH': 3.51,
                'sulphates': 0.56,
                'alcohol': 9.4,
                }):

    if is_ready:
        try:
            input_df = pd.DataFrame(data, index=[0])
            try:
                result = model.predict(input_df)[0]
            except AttributeError:
                 return {'status': 'error', 'reason': 'model'}
            if result==5.02:
                return {'status': 'ok'}
        except NameError:
            return {'status': 'error', 'reason': 'model'}    
    else:
        return {'status': 'error', 'reason': 'unknown'}



@app.post('/predict', response_model=Result)
def predict(data: ModelRequestData):
    input_data = {'fixed_acidity': [data.fixed_acidity],
    'volatile_acidity': [data.volatile_acidity],
    'citric_acid': [data.citric_acid],
    'residual_sugar': [data.residual_sugar],
    'chlorides': [data.chlorides],
    'free_sulfur_dioxide': [data.free_sulfur_dioxide],
    'total_sulfur_dioxide': [data.total_sulfur_dioxide],
    'density': [data.density],
    'pH': [data.pH],
    'sulphates': [data.sulphates],
    'alcohol': [data.alcohol]}

    input_df = pd.DataFrame(input_data, index=[0])
    result = model.predict(input_df)[0]

    return Result(predicted_quality=result)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
    
