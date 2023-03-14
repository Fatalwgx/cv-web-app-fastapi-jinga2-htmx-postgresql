from pydantic import BaseModel


class Token(BaseModel):
    acess_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class User(BaseModel):
    username: str
    password: str
    email: str