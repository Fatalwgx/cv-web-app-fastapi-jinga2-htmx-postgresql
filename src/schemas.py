from pydantic import BaseModel
from datetime import datetime


class Token(BaseModel):
    acess_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class User(BaseModel):
    username: str
    password: str
    email: str

class Player(BaseModel):
    account_id: int
    username: str
    balance: int = None
    games_won: int = None
    games_lost: int = None
    money_spent: int = None
    money_won: int = None
    win_percentage: int = None
    
class UserResponse(BaseModel):
    id: int
    username: str
    last_login: datetime = None

class UserCreatedResponse(BaseModel):
    id: int
    user: str
    email: str