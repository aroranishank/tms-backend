from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.db_init import init_db
from app.routers import auth, tasks, users, stats

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create DB tables on startup
@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(stats.router)

@app.get("/")
def root():
    return {"message": "Task Manager API running"}
