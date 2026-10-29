from fastapi import FastAPI
from pydantic import BaseModel
from app.store import search

app = FastAPI()

class Question(BaseModel):
    question: str
    k: int = 3

@app.post("/search")
def search_endpoint(q: Question):
    return {"question": q.question, "results": search(q.question, q.k)}

@app.get("/")
def health():
    return {"status": "ok"}