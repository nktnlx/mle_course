import streamlit as st
import requests
import time
import pandas as pd
from collections import OrderedDict


# Backend API URL
#API_URL = 'http://0.0.0.0:8080'
API_URL='http://api:8080'

# Helper function to make API requests
def make_api_request(endpoint, method='GET', data=None, params=None, show_error=True):
    try:
        if method == 'GET':
            response = requests.get(f'{API_URL}{endpoint}', params=params)
        elif method == 'POST':
            response = requests.post(f'{API_URL}{endpoint}', json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if show_error:
            st.error(f'Error: {str(e)}')
        return None


# Initialize session state for user authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = None

# Main app
def main():
    st.title('Cardiovascular Disease Probability Prediction Platform')
    # Sidebar for navigation
    if not st.session_state.logged_in:
        menu = ['Login', 'Register']
    else:
        menu = ['Home', 'Make Prediction', 'Transactions History', 'Logout']
    choice = st.sidebar.selectbox('Menu', menu)

    if choice == 'Login':
        login()
    elif choice == 'Register':
        register()
    elif choice == 'Home':
        home()
    elif choice == 'Make Prediction':
        make_prediction()
    elif choice == 'Transactions History':
        transaction_history()
    elif choice == 'Logout':
        logout()


# Login page
def login():
    st.header('Login')
    email = st.text_input('Email')
    password = st.text_input('Password', type='password')
    if st.button('Login'):
        data = {'email': email, 'password': password}
        response = make_api_request('/user/signin', method='POST', data=data)
        if response:
            st.session_state.logged_in = True
            st.session_state.email = email
            st.success('Logged in successfully!')
            time.sleep(1)
            st.rerun()


# Register page
def register():
    st.header('Register')
    name = st.text_input('Name')
    email = st.text_input('Email')
    password = st.text_input('Password', type='password')
    if st.button('Register'):
        data = {'user_name': name, 'email': email, 'password': password}
        response = make_api_request('/user/signup', method='POST', data=data)
        if response:
            st.success('Registered successfully! Please, use Menu to log in.')
            time.sleep(2)
            st.rerun()


# Home page
def home():
    st.header('Welcome! Please, use Menu to: \n- Make Predictions \n- View Transactions History \n- Logout from your account')
    st.write(f'Logged in as: {st.session_state.email}')
    transactions = make_api_request('/transactions', method='GET',
                                    params={'email': st.session_state.email}, show_error=False)
    if transactions:
        ordered_pairs = sorted(
            ((t["id"], round(t["prediction_result"], 4)) for t in transactions["transactions"]),
            key=lambda x: x[0]
        )
        ordered_dict = OrderedDict(ordered_pairs)
        predictions_history = pd.DataFrame(list(ordered_dict.items()),
                                           columns=["Prediction No", "Cardiovascular Disease Probability"])
        #st.line_chart(predictions_history, x='Prediction No', y='Cardiovascular Disease Probability')
        st.subheader("Cardiovascular Disease Probability Predictions History")
        st.line_chart(predictions_history.set_index("Prediction No"))
    else:
        st.write('No predictions history available yet. Make a few predictions to see your progress over time.')


# Make prediction page
def make_prediction():
    st.header('Make Prediction')
    sex = st.selectbox('Sex', ['Male', 'Female'])
    sex = 1 if sex == 'Male' else 0
    age = st.selectbox('Age category', ['Age_18_to_24', 'Age_25_to_29', 'Age_30_to_34',
                                        'Age_35_to_39', 'Age_40_to_44', 'Age_45_to_49',
                                        'Age_50_to_54', 'Age_55_to_59', 'Age_60_to_64',
                                        'Age_65_to_69', 'Age_70_to_74', 'Age_75_to_79',
                                        'Age_80_or_older'])
    general_health = st.selectbox('How will you estimate your overall health condition?', [1, 2, 3, 4, 5])
    weight = st.number_input('What is your weight in kg?', min_value=45, max_value=150, step=1, value=83)
    height = st.number_input('What is your height in meters?', min_value=1.5, max_value=1.95, step=0.01, value=1.71)
    smoking = st.selectbox('Smoker status', ['Former smoker', 'Never smoked',
                                             'Smokes_every_day', 'Smokes_some_days'])
    alcohol = st.selectbox('Alcohol consumption', ['Yes', 'No'])
    alcohol = 1 if alcohol == 'Yes' else 0
    activities = st.number_input('Active days per month', min_value=0, max_value=30, step=1, value=4)
    walking = st.selectbox('Difficulties walking', ['Yes', 'No'])
    walking = 1 if walking == 'Yes' else 0
    sleep = st.number_input('Average sleep hours per night', min_value=3, max_value=11, step=1, value=7)
    checkup = st.selectbox('Last checkup time', ['Past_year', 'Past_2_years', 'Past_5_years', '5_or_more_years_ago'])
    scan = st.selectbox('Chest scan in the last 12 month', ['Yes', 'No'])
    scan = 1 if scan == 'Yes' else 0
    angina = st.selectbox('Had angina in the last 12 month', ['Yes', 'No'])
    angina = 1 if angina == 'Yes' else 0
    teeth = st.selectbox('Had removed teeth in the last 12 month', ['Yes', 'No'])
    teeth = 1 if teeth == 'Yes' else 0
    diabetes = st.selectbox('Do you have diabetes', ['Yes', 'No'])
    diabetes = 1 if diabetes == 'Yes' else 0

    if st.button('Predict'):
        features_data = {
            'HadAngina': int(angina),
            'ChestScan': int(scan),
            'GeneralHealth': int(general_health),
            'AgeCategory': str(age),
            'DifficultyWalking': int(walking),
            'RemovedTeeth': int(teeth),
            'HadDiabetes': int(diabetes),
            'SleepHours': float(sleep),
            'IsMale': int(sex),
            'WeightInKilograms': float(weight),
            'SmokerStatus': str(smoking),
            'HeightInMeters': float(height),
            'AlcoholDrinkers': int(alcohol),
            'LastCheckupTime': str(checkup),
            'PhysicalHealthDays': float(activities)
        }
        request_data = {
            'email': st.session_state.email,
            'data': features_data,
            'model_name': 'catboost'
        }
        response = make_api_request('/prediction', method='POST', data=request_data)
        if response:
            st.success(response['message'])
            time.sleep(2)
            st.write(f'Task ID: {response["task_id"]}')

            # new part with showing prediction results
            st.header('Prediction Results')
            response_result = make_api_request('/result', method='GET',
                                        params={'task_id': response["task_id"]})
            if response_result:
                pred_proba = response_result['prediction_result']
                if pred_proba < 0.25:
                    st.markdown('### 🎉 Congratulations!!! You seem to be a healthy person.')
                    st.write(f'Cardiovascular disease probability: {pred_proba:.2%}')
                elif 0.25 <= pred_proba < 0.5:
                    st.markdown('### 🟢 You are at low risk. It is a good idea to do a checkup from time to time.')
                    st.write(f'Cardiovascular disease probability: {pred_proba:.2%}')
                    st.link_button("SCHEDULE A CHECKUP", "https://helix.ru/catalog/item/40-696")
                elif 0.5 <= pred_proba < 0.75:
                    st.markdown('### 🟡 You are at a moderate risk. We highly recommend to visit a doctor.')
                    st.write(f'Cardiovascular disease probability: {pred_proba:.2%}')
                    st.link_button("MAKE AN APPOINTMENT", "https://prodoctorov.ru/spb/kardiolog/?high_rating=true")
                else:
                    st.markdown("### ⚠️️️⚠️️️⚠️️️️High risk detected!!!⚠️️️⚠️️️⚠️️️")
                    st.write(f'Cardiovascular disease probability: {pred_proba:.2%}')
                    st.link_button("MAKE AN APPOINTMENT ASAP", "https://prodoctorov.ru/spb/kardiolog/?high_rating=true")
                st.write('Visit 🏠Home page to check your predictions history.')


# a helper function to deal with streamlit pyarrow conversion issue
def normalize_data(data):
    if data is None:
        return 'N/A'
    elif isinstance(data, list):
        return ", ".join(str(element) for element in data)
    else:
        return str(data)


# Transaction history page
def transaction_history():
    st.header('Transactions History')
    transactions = make_api_request('/transactions', method='GET',
                                    params={'email': st.session_state.email}, show_error=False)
    if transactions:
        df = pd.DataFrame(transactions['transactions'])
        if 'data' in df.columns:
            df['data'] = df['data'].apply(normalize_data)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(df.sort_values('timestamp', ascending=False),
                     hide_index=True,
                     column_order=('id', 'user_id', 'prediction_result',
                                   'transaction_id', 'data', 'timestamp')
                     )
    else:
        st.write('No transactions found.')


# Logout
def logout():
    st.session_state.logged_in = False
    st.session_state.email = None
    st.success('Logged out successfully!')
    time.sleep(1)
    st.rerun()


if __name__ == '__main__':
    main()
