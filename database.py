from sqlalchemy import create_engine
from sqlmodel import Session
from dotenv import load_dotenv
import os

# if os.getenv("ENVIRONMENT") == "development":
#     DATABASE_URL = "sqlite:///./dev.db"
# else:
#     DATABASE_URL = os.getenv("DATABASE_URL")
#     if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
#         DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


load_dotenv()

if os.getenv("ENVIRONMENT") == "development":
    DATABASE_URL = "sqlite:///./database.db"
else:
    DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

def get_session():
    with Session(engine) as session:
        yield session
