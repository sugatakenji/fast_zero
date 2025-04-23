from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models import User


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
    }
