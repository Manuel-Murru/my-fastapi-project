from sqlmodel import create_engine, SQLModel, Session
from fastapi import Depends
from typing import Annotated

# Nome del file SQLite dove saranno salvati i dati
sqlite_file_name = "app/data/database.db"

# URL di connessione per SQLAlchemy
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Configurazione necessaria per SQLite in modalità multithread (con FastAPI)
connect_args = {"check_same_thread": False}

# Crea il motore del database, che si occuperà delle connessioni
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)

def init_database() -> None:
    SQLModel.metadata.create_all(engine)
#Questa funzione dice a SQLModel di creare tutte le tabelle nel database sulla base dei modelli (class Book(SQLModel) ecc.) che definirai.

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]