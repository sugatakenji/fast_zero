from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!!!'}


def test_exercio_html(client):
    response = client.get('exercicio-html')

    assert response.status_code == HTTPStatus.OK
    assert '<h1>Olá Mundo!</h1>' in response.text


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


def test_create_user_conflict_username(client):
    client.post(
        '/users',
        json={
            'username': 'Fulano',
            'email': 'fulano@test.com',
            'password': 'secret',
        },
    )
    response_post = client.post(
        '/users',
        json={
            'username': 'Fulano',
            'email': 'sicrano@test.com',
            'password': 'mynewpassword',
        },
    )
    assert response_post.status_code == HTTPStatus.CONFLICT
    assert response_post.json() == {'detail': 'Username already exists'}


def test_create_user_conflict_email(client):
    client.post(
        '/users',
        json={
            'username': 'juquinha',
            'email': 'mesmo@test.com',
            'password': 'secret',
        },
    )
    response_post = client.post(
        '/users',
        json={
            'username': 'luquita',
            'email': 'mesmo@test.com',
            'password': 'secret',
        },
    )
    assert response_post.status_code == HTTPStatus.CONFLICT
    assert response_post.json() == {'detail': 'Email already exists'}


def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user_integrity_error(client, user, token):
    client.post(
        '/users',
        json={
            'username': 'Fulano',
            'email': 'fulano@test.com',
            'password': 'secret',
        },
    )
    # update no user.username
    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Fulano',
            'email': 'sicrano@test.com',
            'password': 'mynewpassword',
        },
    )
    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }


def test_update_user(client, user, token):
    reponse = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert reponse.status_code == HTTPStatus.OK
    assert reponse.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': 1,
    }


def test_update_user_not_authorized(client, token):
    response = client.post(
        '/users',
        json={
            'username': 'juquinha',
            'email': 'abrahalinconlis@gmail.com',
            'password': 'asdgaerag',
        },
    )
    user_id = response.json()['id']

    response = client.put(
        f'/users/{user_id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enogh permissions'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_not_authtorized(client, token):
    response = client.post(
        '/users',
        json={
            'username': 'juquinha',
            'email': 'abrahalinconlis@gmail.com',
            'password': 'asdgaerag',
        },
    )
    user_id = response.json()['id']
    response = client.delete(
        f'/users/{user_id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enogh permissions'}


def test_read_user_by_id(client, user):
    response = client.get('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Teste',
        'email': 'teste@teste.com',
        'id': 1,
    }


def test_read_user_by_id_not_found(client, user):
    response = client.get('/users/0')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_login_for_acces_token_not_valid_user(client):
    response = client.post(
        '/token', data={'username': 'invaliduder@test', 'password': '12324rsd'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_login_for_acces_token_wrong_password(client, user):
    response = client.post(
        '/token', data={'username': user.email, 'password': '12324rsd'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}
