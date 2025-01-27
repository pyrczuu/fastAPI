from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from select import select
from models import Task, TaskState, Pomodoro
from database import engine, get_session
from sqlmodel import SQLModel, Session

app = FastAPI()


@app.on_event("startup")
async def startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "Nauka FastAPI"}

@app.post("/tasks")
async def create_task(title:str, description:str, state = TaskState.TO_DO, session: Session = Depends(get_session)):
    task = Task(title=title, description=description, state=state)
    session.add(task)
    session.commit()
    session.refresh(task)
    return {"message": f"Task {task} created"}

@app.get("/tasks")
async def get_tasks(status : str = None, session: Session = Depends(get_session)):
    if status is None:
        return session.exec(select(Task)).all()
    else:
        return session.exec(select(Task)).where(Task.state == status).all()

@app.get("/tasks/{task_id}")
async def get_task(task_id: int, session: Session = Depends(get_session)):
    return session.get(Task,task_id)
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}")
async def update_task(task_id: int,title:str, description:str, state = TaskState.TO_DO, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = title
    task.description = description
    task.state = state
    session.commit()
    session.refresh(task)
    return {"message": f"Task {task} updated"}

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"message": f"Task {task} deleted"}

@app.post("/pomodoro")
async def create_pomodoro(task_id : int, length : int = 25, session: Session = Depends(get_session)):
    if task_id not in session.exec(select(Task.id)).all():
        raise HTTPException(status_code=404, detail="ID does not exist")
    if length <= 0:
        raise HTTPException(status_code=400, detail="Length must be positive")
    pomodoro = session.get(Pomodoro, task_id)
    if not pomodoro.completed:
        raise HTTPException(status_code=404, detail="This task has an active session")
    new_pomodoro = Pomodoro(id = task_id, completed = False, end_time = datetime.now() + timedelta(minutes = length), start_time = datetime.now())
    session.add(new_pomodoro)
    session.commit()
    session.refresh(new_pomodoro)
    return {"message": f"Pomodoro session {new_pomodoro} created"}

@app.post("/pomodoro/{task_id}/stop")
async def stop_pomodoro(task_id : int, session: Session = Depends(get_session)):
    pomodoro = session.get(Pomodoro, task_id)
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Pomodoro not found")
    if pomodoro.completed:
        raise HTTPException(status_code=404, detail="Pomodoro session already stopped")
    pomodoro.end_time = datetime.now()
    pomodoro.completed = True
    session.commit()
    session.refresh(pomodoro)
    return {"message": f"Pomodoro session {id} stopped"}

@app.get("/pomodoro/stats")
async def pomodoro_stats(session: Session = Depends(get_session)):
    stats = ["Zakończone sesje dla każdego zadania: "]
    completed_sessions = {}
    combined_time = 0
    zakonczone = session.exec(select(Pomodoro)).where(Pomodoro.completed == True).all()
    for pomodoro in zakonczone:
        if pomodoro.id in completed_sessions:
            completed_sessions[pomodoro.id] += 1
        else:
            completed_sessions[pomodoro.id] = 1
        combined_time += (pomodoro.end_time - pomodoro.start_time).total_seconds()
    stats.extend(["Spędzone minuty: ", combined_time // 60])
    return stats