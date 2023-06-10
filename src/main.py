import uvicorn
import os

from fastapi import FastAPI, Request, Depends, HTTPException, status, Header
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dotenv import load_dotenv
from enum import Enum
from typing import Annotated

from .auth import AuthHandler
from .schemas import Token, User
from .database import get_db, Base, engine
from .models import Accounts
from . import crud, models, schemas, slots
from utils import files
from .helpers import BaseEnum


# TODO replace plain model and schema calls with models and schemas
# TODO Move logic into external functions and only call it in requests
# TODO Use proper response models


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
    files = "Files"


class Files(str, Enum):
    cv = "lev_zavodskov_cv.pdf"
    recommendation_mpi = "recommendation_mpi.pdf"
    manual_certificate = "manual_certificate.pdf"
    automation_qaguru = "qaguru_certificate.pdf"
    automation_stepik = "stepik_certificate.pdf"
    ef_set_english = "EF_SET_Certificate.pdf"


@app.get("/", response_class=HTMLResponse, tags=[Tags.pages])
async def home_page(request: Request):
    context = {"request": request, "present": datetime.now().strftime("%d.%m.%Y")}
    return templates.TemplateResponse("home.html", context)


@app.get("/api", response_class=HTMLResponse, tags=[Tags.pages])
async def api_page(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("api_docs.html", context)


@app.get("/files", tags=[Tags.pages], response_class=HTMLResponse)
async def files_page(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("files.html", context)


@app.get("/projects/slots", tags=[Tags.slots, Tags.pages])
async def slots_page(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("slots.html", context)


@app.get("/login", response_class=HTMLResponse, tags=[Tags.pages])
async def login_page(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("login.html", context)


@app.post("/user/login", response_model=Token, tags=[Tags.user])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = auth_handler.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or passowrd",
        )
    access_token_expires = timedelta(minutes=auth_handler.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_handler.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    crud.update_login_date(db, form_data.username)
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.post(
    "/user/register", response_model=schemas.UserCreatedResponse, tags=[Tags.user]
)
def create_user(user: User, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username taken"
        )
    created_user = crud.create_user(db=db, user=user)
    return schemas.UserCreatedResponse(
        id=created_user.id, username=created_user.username, email=created_user.email
    )


@app.get("/user", response_model=schemas.UserResponse, tags=[Tags.user])
async def fetch_user_info(
    access_token: Annotated[str, Header()] = None, db: Session = Depends(get_db)
):
    user = auth_handler.get_current_user(db, access_token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    return schemas.UserResponse(
        id=user.id, username=user.username, last_login=user.last_login
    )


@app.put("/user/edit", response_model=schemas.UserUpdateResponse, tags=[Tags.user])
async def edit_user_info(
    user_data: schemas.UserUpdate,
    access_token: Annotated[str, Header()] = None,
    password: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
):
    user = crud.update_user(
        db=db, user_data=user_data, access_token=access_token, password=password
    )
    return schemas.UserUpdateResponse(
        id=user.id, username=user.username, email=user.email
    )


@app.get("/slots/start", tags=[Tags.slots], response_class=HTMLResponse)
async def start_slots_game(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("lines.html", context)


@app.get("/slots/spin", tags=[Tags.slots])
async def do_spin(request: Request):
    columns, winnings = slots.spin()
    context = {"request": request, "winnings": winnings, "columns": columns}
    return templates.TemplateResponse("lines.html", context)


@app.get("/files/{file}", tags=[Tags.files], response_class=FileResponse)
async def get_file(file: Files):
    for item in Files:
        if file is item:
            return files.to_resource(item.value)
