from sqlalchemy import Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql.schema import Column
from sqlalchemy.orm import relationship, backref
from .database import Base
from datetime import datetime


class Accounts(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(250), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    created_on = Column(TIMESTAMP, nullable=False, default=datetime.now())
    last_login = Column(TIMESTAMP, nullable=True, server_default=None)

    stats = relationship("Stats", backref=backref('accounts', uselist=True))
    vault = relationship("Vault", backref=backref('accounts', uselist=True))

class Stats(Base):
    __tablename__ = 'stats'

    account_id = Column(Integer, ForeignKey(Accounts.id), primary_key=True)
    games_won = Column(Integer, nullable=False, default=0)
    games_lost = Column(Integer, nullable=False, default=0)
    win_percentage = Column(Integer, nullable=True, server_default=None)
    money_spent = Column(Integer, nullable=False, default=0)
    money_won = Column(Integer, nullable=False, default=0)

class Vault(Base):
    __tablename__ = 'vault'

    account_id = Column(Integer, ForeignKey(Accounts.id), primary_key=True)
    balance = Column(Integer, nullable=False, default=100)
