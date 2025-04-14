from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserDB(BaseModel):
    username: str
    email: EmailStr
    password: str
    id: int


class UsersList(BaseModel):
    users: list[UserPublic]
