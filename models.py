from typing import Optional
from enum import Enum
from sqlmodel import Field, SQLModel
from datetime import datetime


class TaskState(str, Enum):
    TO_DO = "do wykonania"
    IN_PROGRESS = "w trakcie"
    FINISHED = "zakończone"

class Task(SQLModel, table = True):
    id: Optional[int] = Field(primary_key=True, index=True)
    title: str = Field(min_length = 3, max_length=100, unique=True)
    description: Optional[str] = Field(default="brak opisu", max_length=300)
    state: TaskState = TaskState.TO_DO

    def __str__(self):
        return self.title

class Pomodoro(SQLModel, table = True):
    id: Optional[int] = Field(primary_key=True, index=True)
    completed: bool = Field(default=False)
    start_time: datetime = Field(default=datetime.now())
    end_time: datetime

    def __str__(self):
        return self.id

