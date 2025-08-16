from fastapi import status


def test_signup_success(client):
    user_data = {
        'user_name': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword',
    }
    response = client.post('/user/signup', json=user_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'User successfully created!'}


def test_signup_duplicate_email(client, test_user):
    user_data = {
        'user_name': 'duplicateuser',
        'email': test_user.email,  # Use existing email
        'password': 'newpassword',
    }
    response = client.post('/user/signup', json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert 'User with this email already exists' in response.json()['detail']


def test_signin_success(client, test_user):
    login_data = {
        'email': test_user.email,
        'password': 'testpassword',
    }
    response = client.post('/user/signin', json=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['message'] == 'User signed in successfully.'


def test_signin_invalid_credentials(client, test_user):
    login_data = {
        'email': test_user.email,
        'password': 'wrongpassword',
    }
    response = client.post('/user/signin', json=login_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'Wrong credentials passed' in response.json()['detail']


def test_get_all_users(client, test_user):
    response = client.get('/user/users')
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert len(users) == 1
    assert any(user['email'] == test_user.email for user in users)
