from . import schemas, models
from sqlalchemy.orm import Session
from .auth import AuthHandler
from datetime import datetime


auth_handler = AuthHandler()


def get_user_by_username(db: Session, username: str):
    return db.query(models.Accounts).filter(models.Accounts.username == username).first()

def create_user(db: Session, user: schemas.User):
    db_user = models.Accounts(
        username=user.username,
        hashed_password=auth_handler.get_password_hash(user.password),
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_login_date(db: Session, username: str):
    user = get_user_by_username(db, username)
    user.last_login = datetime.now()
    db.commit()
    db.refresh(user)
    return user.last_login
