from sqlmodel import SQLModel, Field
from typing import Annotated

class BookBase(SQLModel):
    # Superclasse con attributi comuni a tutti i modelli
    title: str
    author: str
    review: Annotated[int | None, Field(ge=1, le=5)] = None

class Book(BookBase, table=True):
    # Modello relazionale per il database
    id: int = Field(default=None, primary_key=True)

class BookCreate(BookBase):
    # Schema per creare un nuovo libro (senza ID)
    pass

class BookPublic(BookBase):
    # Schema per restituire un libro completo con ID
    id: int


