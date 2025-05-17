from fastapi import APIRouter, Path, HTTPException, Query, Form
from typing import Annotated, List
from app.models.book import Book, BookCreate, BookPublic
from app.models.review import Review
from pydantic import ValidationError
from data.db import SessionDep
from sqlmodel import select

router = APIRouter(prefix="/books")

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
    session.exec(select(Book)).delete()
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



@router.post("/_form/")
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
