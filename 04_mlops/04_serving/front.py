import streamlit as st
import requests

# URL of your FastAPI application
FASTAPI_URL = "http://localhost:8000"

st.title('Wine Quality Prediction')

# Input fields for all wine features
fixed_acidity = st.number_input('Fixed Acidity', min_value=0.0, value=7.4, step=0.1)
volatile_acidity = st.number_input('Volatile Acidity', min_value=0.0, value=0.7, step=0.01)
citric_acid = st.number_input('Citric Acid', min_value=0.0, value=0.0, step=0.01)
residual_sugar = st.number_input('Residual Sugar', min_value=0.0, value=1.9, step=0.1)
chlorides = st.number_input('Chlorides', min_value=0.0, value=0.076, step=0.001)
free_sulfur_dioxide = st.number_input('Free Sulfur Dioxide', min_value=0, value=11, step=1)
total_sulfur_dioxide = st.number_input('Total Sulfur Dioxide', min_value=0, value=34, step=1)
density = st.number_input('Density', min_value=0.0, value=0.9978, step=0.0001)
pH = st.number_input('pH', min_value=0.0, value=3.51, step=0.01)
sulphates = st.number_input('Sulphates', min_value=0.0, value=0.56, step=0.01)
alcohol = st.number_input('Alcohol', min_value=0.0, value=9.4, step=0.1)

# Button to make prediction
if st.button('Predict Quality'):
    # Form the request payload
    payload = {
        'fixed_acidity': fixed_acidity,
        'volatile_acidity': volatile_acidity,
        'citric_acid': citric_acid,
        'residual_sugar': residual_sugar,
        'chlorides': chlorides,
        'free_sulfur_dioxide': free_sulfur_dioxide,
        'total_sulfur_dioxide': total_sulfur_dioxide,
        'density': density,
        'pH': pH,
        'sulphates': sulphates,
        'alcohol': alcohol
    }

    # Send the POST request to your FastAPI app
    response = requests.post(f"{FASTAPI_URL}/predict/", json=payload)
    if response.status_code == 200:
        prediction = response.json()['predicted_quality']
        st.success(f'Predicted Wine Quality: {prediction}')
    else:
        st.error('Error in prediction')

# HealthCheck Button
if st.button('Health Check'):
    response = requests.get(f"{FASTAPI_URL}/healthcheck")

    if <все хорошо>:
        st.success("Healthy")
    else:
        st.error(<текст ошибки>)
