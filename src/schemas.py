from pydantic import BaseModel, validator, ValidationError
from datetime import datetime
from fastapi import HTTPException, status
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class User(BaseModel):
    username: str
    password: str
    email: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None

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
    username: str
    email: str

class UserUpdateResponse(BaseModel):
    id: int
    username: str = None
    email: str = None
