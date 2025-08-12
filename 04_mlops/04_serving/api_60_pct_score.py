import uvicorn
import joblib
import subprocess

import pandas as pd
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel


try:
    subprocess.run(['dvc', 'pull'], check=True)
    #print('Model loaded successfully!')
except subprocess.CalledProcessError as e:
    #print(f'Failed to load the model: {e}')
    pass


with open('model.pkl', 'rb') as file:
    model = joblib.load(file)
    #print('Model opened from pkl file.')


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
    #print(input_df)
    result = model.predict(input_df)[0]
    #print('Im here!')
    return Result(predicted_quality=result)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
