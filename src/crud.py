from . import schemas, models, slots
from sqlalchemy.orm import Session
from .auth import AuthHandler
from datetime import datetime


auth_handler = AuthHandler()


def get_user_by_username(db: Session, username: str):
    return db.query(models.Accounts).filter(models.Accounts.username == username).first()

def get_user_by_id(db: Session, id: int):
    return db.query(models.Accounts).filter(models.Accounts.id == id).first()

def create_user(db: Session, user: schemas.User):
    created_user = models.Accounts(
        username=user.username,
        hashed_password=auth_handler.get_password_hash(user.password),
        email=user.email
    )
    db.add(created_user)
    db.commit()
    db.refresh(created_user)
    return created_user

def update_user(db: Session, user_data: schemas.UserUpdate, access_token: str, password: str):
    user = auth_handler.get_current_user(db, access_token)
    authenticated_user = auth_handler.authenticate_user(db=db, username=user.username, password=password)
    if user_data.username:
        authenticated_user.username = user_data.username
    if user_data.email:
        authenticated_user.email = user_data.email
    if user_data.password:
        authenticated_user.hashed_password = auth_handler.get_password_hash(user_data.password)
    db.commit()
    db.refresh(authenticated_user)
    return authenticated_user

def update_login_date(db: Session, username: str):
    user = get_user_by_username(db, username)
    user.last_login = datetime.now()
    db.commit()
    db.refresh(user)
    return user.last_login

def do_spin(db: Session):
    slots.spin()
