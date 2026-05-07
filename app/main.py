from fastapi import FastAPI

from app.db.database import engine, Base
from app.routers import tasks, auth, users



Base.metadata.create_all(engine)


app = FastAPI()

app.include_router(tasks.router)
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to task manager"}