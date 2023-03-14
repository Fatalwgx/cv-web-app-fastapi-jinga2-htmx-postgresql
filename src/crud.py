from . import schemas, models
from sqlalchemy.orm import Session
from .auth import AuthHandler


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
