from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models import Todo, User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(username='leopoldo', password='123', email='test@test')
        session.add(new_user)
        await session.commit()

    user = await session.scalar(
        select(User).where(User.username == 'leopoldo')
    )

    assert asdict(user) == {
        'id': 1,
        'username': 'leopoldo',
        'password': '123',
        'email': 'test@test',
        'created_at': time,
        'update_at': time,
        'todos': [],
    }


@pytest.mark.asyncio
async def test_create_todo(session, user, mock_db_time):
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='draft',
        user_id=user.id,
    )
    session.add(todo)
    await session.commit()

    todo = await session.scalar(select(Todo))

    assert todo.title == 'Test Todo'
    assert todo.description == 'Test Desc'
    assert todo.state == 'draft'
    assert todo.user_id == user.id


@pytest.mark.asyncio
async def test_user_todo_relationship(session, user: User):
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='draft',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(User.id == user.id))

    assert user.todos == [todo]
