from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel
import os

# if os.getenv("ENVIRONMENT") == "development":
#     DATABASE_URL = "sqlite:///./dev.db"
# else:
#     DATABASE_URL = os.getenv("DATABASE_URL")
#     if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
#         DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


if os.getenv("ENVIRONMENT") == "production":
    DATABASE_URL = os.getenv("DATABASE_URL")
else:
    DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(DATABASE_URL)

# SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session