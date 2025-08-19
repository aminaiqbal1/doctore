from fastapi import FastAPI
from routers import file_upload, user, patient
from fastapi.middleware.cors import CORSMiddleware 
from database import engine, Base

# This command creates your tables if they don't already exist
Base.metadata.create_all(bind=engine) 

app = FastAPI()

@app.get("/")
def home():
    return {"msg": "App is running!"}

# Your existing CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(patient.router) 
app.include_router(file_upload.router)  


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


    #alembic revision --autogenerate -m "update user patient and chat history table" 
    # alembic upgrade head

    # validation ka lia hum pydantic model ki validation ko use krty hain validation do trhn ki hoti hai ak db leveal aur ak pydantic model say jo input lananyn wali class banaty hain us level pr kr skty hain level 
    # db level pr validation ka lia hum sqlalchemy ki class banaty hain aur pydantic model pr validation ka lia hum pydantic ki class banaty hain
    