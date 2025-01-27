from sqlalchemy import create_engine
from sqlmodel import Session

DATABASE_URL = "sqlite:///./dev.db"
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

def get_session():
    with Session(engine) as session:
        yield session
