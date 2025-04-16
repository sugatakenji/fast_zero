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


def test_update_user_integrity_error(client, user):
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


def test_update_user(client, user):
    reponse = client.put(
        '/users/1',
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


def test_update_user_not_found(client):
    response = client.put(
        '/users/20',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client, user):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_note_foud(client):
    response = client.delete('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


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
