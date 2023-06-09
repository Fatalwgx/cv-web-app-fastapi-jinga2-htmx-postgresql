from . import schemas, models, slots
from sqlalchemy.orm import Session
from .auth import AuthHandler
from datetime import datetime


auth_handler = AuthHandler()


def get_user_by_username(db: Session, username: str):
    return db.query(models.Accounts).filter(models.Accounts.username == username).first()

def get_user_by_id(db: Session, id: int, access_token):
    user = auth_handler.get_current_user(db, access_token)

def create_user(db: Session, user: schemas.User):
    db_user = models.Accounts(
        username=user.username,
        hashed_password=auth_handler.get_password_hash(user.password),
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return schemas.UserCreatedResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email
    )

def update_login_date(db: Session, username: str):
    user = get_user_by_username(db, username)
    user.last_login = datetime.now()
    db.commit()
    db.refresh(user)
    return user.last_login

def do_spin(db: Session, ):
    slots.spin()
