from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import ask_question
from logger import log_sample
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
def query_rag(request: QueryRequest):
    result = ask_question(request.question)

    sample = {
        "question": request.question,
        "answer": result["answer"],
        "contexts": result["contexts"]
    }

    log_sample(sample)

    return result