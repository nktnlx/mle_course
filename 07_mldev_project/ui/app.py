import streamlit as st
import requests
import time
import pandas as pd


# Backend API URL
#API_URL = 'http://0.0.0.0:8080'
API_URL='http://api:8080'

# Helper function to make API requests
def make_api_request(endpoint, method='GET', data=None, params=None):
    try:
        if method == 'GET':
            response = requests.get(f'{API_URL}{endpoint}', params=params)
        elif method == 'POST':
            response = requests.post(f'{API_URL}{endpoint}', json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f'Error: {str(e)}')
        return None


# Initialize session state for user authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = None
    st.session_state.is_admin = False

# Main app
def main():
    st.title('Titanic Survival Probability Prediction Platform')
    # Sidebar for navigation
    if not st.session_state.logged_in:
        menu = ['Login', 'Register']
    else:
        menu = ['Home', 'Add Balance', 'Make Prediction', 'Transactions History', 'Logout']
    choice = st.sidebar.selectbox('Menu', menu)

    if choice == 'Login':
        login()
    elif choice == 'Register':
        register()
    elif choice == 'Home':
        home()
    elif choice == 'Add Balance':
        add_balance()
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
            st.session_state.is_admin = response.get('is_admin', False)
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
    st.header('Welcome! Please, use Menu to: \n- Add Balance \n- Make Predictions \n- view Transactions History')
    st.write(f'Logged in as: {st.session_state.email}')
    balance = make_api_request('/balance', method='GET', params={'email': st.session_state.email})
    if balance:
        st.write(f'Current Balance: ${round(balance["balance"], 2)}')


# Add balance page
def add_balance():
    st.header('Add Balance')
    amount = st.number_input('Amount', min_value=1.00, step=0.5, value=10.0)
    target_email = None
    if st.session_state.is_admin:
        target_email = st.text_input('Target Email (optional, for admins only)')
    if st.button('Add Balance'):
        data = {'email': st.session_state.email, 'amount': amount}
        if target_email:
            data['target_email'] = target_email
        response = make_api_request('/balance', method='POST', data=data)
        if response:
            result_message = f'{response["message"]} New Balance: ${round(response["new_balance"], 2)}.'
            st.success(result_message)
            time.sleep(2)
            st.rerun()


# Make prediction page
def make_prediction():
    st.header('Make Prediction')
    sex = st.selectbox('Sex', ['male', 'female'])
    age = st.number_input('Age', min_value=1, max_value=130, step=1, value=35)
    is_alone = st.selectbox('Is Alone', ['0', '1'])
    pclass = st.selectbox('Passenger Class', ['1', '2', '3'])
    fare = st.number_input('Fare', min_value=10.0, step=0.5)
    if st.button('Predict'):
        features_data = {
            'sex': str(sex),
            'age': int(age),
            'is_alone': str(is_alone),
            'pclass': str(pclass),
            'fare': float(fare)
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
            st.write(f'Balance before prediction: ${round(response["balance_before_prediction"], 2)}')

            # new part with showing prediction results
            st.header('Prediction Results')
            response_result = make_api_request('/result', method='GET',
                                        params={'task_id': response["task_id"]})
            response_balance = make_api_request('/balance', method='GET',
                                                params={'email': st.session_state.email})
            if response_result and response_balance:
                pred_proba = response_result['prediction_result']
                if pred_proba >= 0.5:
                    st.markdown('### 🟢 You have a good chance to survive!')
                    st.write(f'Survival probability: {pred_proba:.2%}')
                else:
                    st.markdown("### ☠️ Most likely you won't make it.")
                    st.write(f'Survival probability: {pred_proba:.2%}')
                st.write(f'Balance after prediction: ${round(response_balance["balance"], 2)}')


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
    transactions = make_api_request('/transactions', method='GET', params={'email': st.session_state.email})
    if transactions:
        df = pd.DataFrame(transactions['transactions'])
        if 'data' in df.columns:
            df['data'] = df['data'].apply(normalize_data)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(df.sort_values('timestamp', ascending=False),
                     hide_index=True,
                     column_order=('id', 'user_id', 'data', 'prediction_result',
                                   'transaction_type', 'amount', 'timestamp', 'transaction_id' ,'is_admin')
                     )
    else:
        st.write('No transactions found.')


# Logout
def logout():
    st.session_state.logged_in = False
    st.session_state.email = None
    st.session_state.is_admin = False
    st.success('Logged out successfully!')
    time.sleep(1)
    st.rerun()


if __name__ == '__main__':
    main()
