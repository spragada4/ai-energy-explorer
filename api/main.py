# api/main.py
from fastapi import FastAPI
from api.routes import predict

app = FastAPI(title="AI Energy Efficiency Explorer API")

app.include_router(predict.router)

@app.get("/health")
def health():
    return {"status": "ok"}