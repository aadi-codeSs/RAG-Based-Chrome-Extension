from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import rag_pipeline

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    question: str
    context: str


class Answer(BaseModel):
    answer: str


@app.get("/")
def health_check():
    return {"status": "ok", "message": "RAG Browser Assistant API is running"}


@app.post("/ask", response_model=Answer)
def ask(query: Query):
    try:
        answer = rag_pipeline(
            query.context, 
            query.question
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "answer": answer
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
