from fastapi import FastAPI
from routes import analyze
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="home")

app.include_router(analyze.router)

@app.get("/")
def read_root():
    return {"message": "App is running"}
