import uvicorn
import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dotenv import load_dotenv
from enum import Enum
from .auth import AuthHandler
from .schemas import Token, User
from .database import get_db, Base, engine
from .models import Accounts
from . import crud, models, schemas


#TODO replace plain model and schema calls with models. schemas.


load_dotenv()
Base.metadata.create_all(bind=engine)


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
auth_handler = AuthHandler()


class Tags(Enum):
    pages = "Pages"
    user = "User"
    slots = "Slots"
    editor = "Editor"
    projects = "Projects"


@app.get("/", response_class=HTMLResponse, tags=[Tags.pages])
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "present": datetime.now().strftime('%d.%m.%Y')})


@app.get("/api", response_class=HTMLResponse, tags=[Tags.pages])
async def api_page(request: Request):
    return templates.TemplateResponse("api_docs.html", {"request": request})


@app.get("/projects/slots", tags=[Tags.slots, Tags.pages])
async def slots_page(request: Request):
    return templates.TemplateResponse("slots.html", {"request": request})


@app.post("/user/token", response_model=Token, tags=[Tags.user])
async def login_for_acces_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_handler.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or passowrd")
    access_token_expires = timedelta(minutes=auth_handler.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_handler.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    crud.update_login_date(db, form_data.username)
    return {"acess_token": access_token, "token_type": "bearer"}


@app.post("/users/", tags=[Tags.user])
def create_user(user: User, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username taken")
    return crud.create_user(db=db, user=user)

@app.get('/user', tags=[Tags.user])
async def fetch_user_info(access_token: str, db: Session = Depends(get_db)):
    user = auth_handler.get_current_user(db, access_token)
    return {user}

@app.get("/slots/start", tags=[Tags.slots], response_class=HTMLResponse)
async def start_slots_game(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("lines.html", context)

# 11512124