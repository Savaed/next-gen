from fastapi import FastAPI

app = FastAPI()

@app.get("/api/ping")
async def pong():
    return "pong"
