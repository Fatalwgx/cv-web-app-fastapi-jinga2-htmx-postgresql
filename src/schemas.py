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

class Player(BaseModel):
    account_id: int
    username: str
    balance: int
    games_won: int
    games_lost: int
    money_spent: int
    money_won: int
    win_percentage: int
    