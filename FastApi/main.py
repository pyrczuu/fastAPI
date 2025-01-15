from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from typing import ClassVar, Optional
app = FastAPI()

class TaskState(str, Enum):
    TO_DO = "do wykonania"
    IN_PROGRESS = "w trakcie"
    FINISHED = "zakończone"

class Task(BaseModel):
    id : int = 0
    title : str = Field(min_length = 3, max_length=100)
    description : Optional[str] = Field(default="brak opisu", max_length=300)
    state : TaskState = TaskState.TO_DO
    task_counter : ClassVar[int] = 0

tasks = []
pomodoro_sessions = [
    # {
    #     "task_id": 1,
    #     "start_time": "2025-01-14T22:22:00",
    #     "end_time": "2025-01-14T22:25:00",
    #     "completed": False
    # }
]

def title_validator(title):
    titles = list(map(lambda task:task.title ,tasks))
    if title not in titles:
        return title
    raise HTTPException(status_code=400, detail="Title must be unique")
@app.get("/")
async def root():
    return {"message": "Nauka FastAPI"}

@app.post("/tasks")
async def create_task(task: Task):
    task.title = title_validator(task.title)
    Task.task_counter += 1
    task.id = Task.task_counter
    tasks.append(task)
    return {"message": "Task created"}

@app.get("/tasks")
async def get_tasks(status : str = None):
    if status is None:
        return tasks
    else:
        filtered_tasks = []
        for task in tasks:
            if task.state == status:
                filtered_tasks.append(task)
        return filtered_tasks


@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, updated_task: Task):
    for task in tasks:
        if task.id == task_id:
            task.title = title_validator(updated_task.title)
            task.description = updated_task.description
            task.state = updated_task.state
            return {"message": f"Task {task_id} updated. Title: {task.title} Description: {task.description} State: {task.state}"}
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return {"message": f"Task {task_id} deleted"}
    raise HTTPException(status_code=404, detail="Task not found")

def update_all_timers():
    for timer in pomodoro_sessions:
        if datetime.fromisoformat(timer["end_time"]) <= datetime.now():
            timer["completed"] = True

@app.post("/pomodoro")
async def create_pomodoro(task_id : int, length : int = 25):
    update_all_timers()
    if length <= 0:
        raise HTTPException(status_code=400, detail="Length must be positive")
    for pomodoro in pomodoro_sessions:
        if pomodoro["task_id"] == task_id and pomodoro["completed"] is False:
            raise HTTPException(status_code=404, detail="This task has an active session")
    for task in tasks:
        if task.id == task_id:
            pomodoro_sessions.append({"task_id": task_id, "start_time": str(datetime.now()), "end_time": str(datetime.now() + timedelta(minutes=length)),
                                      "completed": False})
            return {"message": "Pomodoro session created"}
    raise HTTPException(status_code=404, detail="ID does not exist")

@app.post("/pomodoro/{task_id}/stop")
async def stop_pomodoro(task_id : int):
    update_all_timers()
    for session in pomodoro_sessions:
        if session["task_id"] == task_id:
            session["end_time"] = str(datetime.now())
            if session["completed"] is True:
                raise HTTPException(status_code=404, detail="Pomodoro session already stopped")
            session["completed"] = True
            return {"message": "Pomodoro session stopped"}
    raise HTTPException(status_code=404, detail="ID does not exist")

@app.get("/pomodoro/stats")
async def pomodoro_stats():
    stats = []
    completed_sessions = {}
    combined_time = 0
    for session in pomodoro_sessions:
        if session["completed"]:
            if session["task_id"] in completed_sessions:
                completed_sessions[session["task_id"]] += 1
            else:
                completed_sessions[session["task_id"]] = 1
            combined_time += (datetime.fromisoformat(session["end_time"]) - datetime.fromisoformat(session["start_time"])).total_seconds()
    stats.append(completed_sessions)
    stats.append({"Combined Time in Minutes": combined_time // 60})
    return stats