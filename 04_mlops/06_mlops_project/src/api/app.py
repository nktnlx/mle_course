import json
import os
import subprocess
from http.client import HTTPException

import joblib
import pandas as pd
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, confloat


def pull_latest_model(model_dir):
    try:
        os.chdir(model_dir)
        subprocess.run(['dvc', 'pull'], check=True)
        print('Model pulled successfully.')
    except subprocess.CalledProcessError as e:
        print(f'Error pulling model from DVC: {e}')
        raise HTTPException(500, 'Failed to pull model from DVC')


def load_model(path):
    try:
        with open(path, 'rb') as file:
            model = joblib.load(file)
            return model
    except FileNotFoundError:
        pass


MODEL_DIR = '/Users/nikitin_a/PycharmProjects/mlops_wine_project/models'
MODEL_PATH = '/Users/nikitin_a/PycharmProjects/mlops_wine_project/models/rf_model.pkl'

is_ready = True
pull_latest_model(MODEL_DIR)
model = load_model(MODEL_PATH)
print('Model loaded successfully.')

app = FastAPI()


class WineFeatures(BaseModel):
    fixed_acidity: confloat(ge=0)
    volatile_acidity: confloat(ge=0)
    citric_acid: confloat(ge=0)
    residual_sugar: confloat(ge=0)
    chlorides: confloat(ge=0)
    free_sulfur_dioxide: confloat(ge=0)
    total_sulfur_dioxide: confloat(ge=0)
    density: confloat(ge=0)
    pH: confloat(ge=0)
    sulphates: confloat(ge=0)
    alcohol: confloat(ge=0)


class Result(BaseModel):
    predicted_quality: float


@app.get('/health')
def health(
    data={
        'fixed_acidity': 7.4,
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
    }
):
    if is_ready:
        try:
            input_df = pd.DataFrame(data, index=[0])
            try:
                result = model.predict(input_df)[0]
            except AttributeError:
                return {'status': 'error', 'reason': 'model'}
            if result == 5.818:
                return {'status': 'ok'}
        except NameError:
            return {'status': 'error', 'reason': 'model'}
    else:
        return {'status': 'error', 'reason': 'unknown'}


@app.get('/model-info')
def model_info() -> dict:
    try:
        metadata_path = '/Users/nikitin_a/PycharmProjects/mlops_wine_project/models/rf_model_metadata.json'
        with open(metadata_path, 'r') as f:
            model_metadata = json.load(f)
        return model_metadata
    except FileNotFoundError:
        raise HTTPException(500, 'Failed to load metadata.')


@app.post('/predict', response_model=Result)
def predict(data: WineFeatures):
    input_data = {
        'fixed_acidity': [data.fixed_acidity],
        'volatile_acidity': [data.volatile_acidity],
        'citric_acid': [data.citric_acid],
        'residual_sugar': [data.residual_sugar],
        'chlorides': [data.chlorides],
        'free_sulfur_dioxide': [data.free_sulfur_dioxide],
        'total_sulfur_dioxide': [data.total_sulfur_dioxide],
        'density': [data.density],
        'pH': [data.pH],
        'sulphates': [data.sulphates],
        'alcohol': [data.alcohol],
    }
    try:
        input_df = pd.DataFrame(input_data, index=[0])
        result = model.predict(input_df)[0]
        return Result(predicted_quality=result)
    except Exception as e:
        raise HTTPException(500, 'Failed to make prediction.')


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
