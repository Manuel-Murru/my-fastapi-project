from fastapi import APIRouter, Path, HTTPException, Query, Form, UploadFile
from typing import Annotated, List
from app.models.book import Book, BookCreate, BookPublic
from app.models.review import Review
from pydantic import ValidationError
from app.data.db import SessionDep, sqlite_file_name
from sqlmodel import select, delete
from fastapi.responses import StreamingResponse, FileResponse
from io import BytesIO

router = APIRouter(prefix="/books")

@router.get("/download_db", response_class=FileResponse, name="download_db")
async def download_db() -> FileResponse:
    """Returns the DB file"""
    headers = {"Content-Disposition": f"attachment; filename=database.db"}
    return FileResponse(sqlite_file_name, headers=headers)

@router.get("/")
def get_all_books(
    session: SessionDep,
    sort: Annotated[bool, Query(description="Sort books by their review")] = False
) -> list[BookPublic]:
    """Returns the list of available books."""
    books = session.exec(select(Book)).all()

    if sort:
        books = sorted(books, key=lambda book: book.review if book.review is not None else -1)

    # Convertiamo ogni Book (modello relazionale) in BookPublic (schema API)
    return [BookPublic.model_validate(book) for book in books]


@router.get("/{id}")
def get_book_by_id(
    session: SessionDep,
    id: Annotated[int, Path(description="The ID of the book to get")]
) -> BookPublic:
    """Returns the book with the given ID."""
    book = session.get(Book, id)
    if book:
        return book
    else:
        raise HTTPException(status_code=404, detail="Book not found")


@router.post("/{id}/review")
def add_review(
        session: SessionDep,
        id: Annotated[int, Path(description="The ID of the book to which add the review")],
        review: Review
):
    """Adds a review to the book with the given ID."""
    book = session.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book.review = review.review
    session.commit()
    return "Review successfully added"


@router.post("/")
def add_book(session: SessionDep, book: BookCreate):
    """Adds a new book."""
    # Convertiamo il BookCreate (API schema) in Book (modello DB)
    new_book = Book.model_validate(book)

    session.add(new_book)  # Inserisce il nuovo oggetto nella sessione
    session.commit()       # Rende effettiva la modifica nel DB
    session.refresh(new_book)  # Aggiorna l'oggetto con l'ID assegnato dal DB

    return {"message": "Book successfully added", "book": new_book}

@router.put("/{id}")
def update_book(
    session: SessionDep,
    id: Annotated[int, Path(description="The ID of the book to update")],
    new_book: BookCreate
):
    """Updates the book with the given ID."""
    book = session.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book.title = new_book.title
    book.author = new_book.author
    book.review = new_book.review
    session.add(book)
    session.commit()
    return "Book successfully updated"



@router.delete("/")
def delete_all_books(session: SessionDep):
    """Deletes all the stored books."""
    statement = delete(Book)
    session.exec(statement)
    session.commit()
    return "All books successfully deleted"


@router.delete("/{id}")
def delete_book(
    session: SessionDep,
    id: Annotated[int, Path(description="The ID of the book to delete")]
):
    """Deletes the book with the given ID."""
    book = session.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    return "Book successfully deleted"



@router.post("/_form/", name="add_book_from_form")
def add_book_from_form(
    session: SessionDep,
    title: Annotated[str, Form()],
    author: Annotated[str, Form()],
    review: Annotated[int | None, Form()] = None
):
    """Adds a new book from form data."""
    book_data = BookCreate(title=title, author=author, review=review)

    session.add(Book.model_validate(book_data))
    session.commit()

    return "Book successfully added"


@router.get("/{id}/download", response_class=StreamingResponse, name="download_book")
async def download_book(
        session: SessionDep,
        id: Annotated[int, Path(description="The ID of the book to download")]
) -> StreamingResponse:
    """Returns as a JSON file the book with the given ID."""
    book = session.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    buffer = BytesIO(book.model_dump_json().encode("utf-8"))
    headers = {"Content-Disposition": f"attachment; filename={book.title}.json"}
    return StreamingResponse(buffer, headers=headers, media_type="application/octet-stream")

@router.post("/_file/", name="add_book_from_file")
async def add_book_from_file(
    session: SessionDep,
    file: UploadFile,
):
    """Adds a new book from a JSON file upload."""
    try:
        contents = await file.read()
        book = Book.model_validate_json(contents)
        session.add(book)
        session.commit()
        return {"message": "Book successfully added from file", "book": book}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid file or data: {e}")