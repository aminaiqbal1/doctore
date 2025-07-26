from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth_router, health_router, progress_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Health Assistant API")
@app.get("/")
def read_root():
    return {"message": "Welcome to AI Health Assistant API"}
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router)
app.include_router(health_router.router)
app.include_router(progress_router.router)

