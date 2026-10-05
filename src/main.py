from fastapi import FastAPI

app = FastAPI()

@app.get("/search")
async def root():
    return {"message": "Hello World"}