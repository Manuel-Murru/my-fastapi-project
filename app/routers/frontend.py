from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from data.db import SessionDep
from sqlmodel import select
from app.models.book import Book


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Rotta per la home page
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    text = {"message": "Welcome to the library"}
    return templates.TemplateResponse(
        name="home.html",
        context={"request": request, "text": text}
    )

# Rotta per la lista dei libri
@router.get("/book_list", response_class=HTMLResponse, name="show_book_list")
def show_book_list(request: Request, session: SessionDep):
    books = session.exec(select(Book)).all()
    context = {"request": request, "books": books}
    return templates.TemplateResponse(name="list.html", context=context)


@router.get("/add_book", response_class=HTMLResponse)
def add_book_form(request: Request):
    return templates.TemplateResponse(
        request=request, name="add.html"
 )
