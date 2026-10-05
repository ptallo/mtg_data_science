from fastapi import FastAPI
from services.container import Container

container: Container = Container.get_singleton()
app = FastAPI()

@app.get("/search")
async def root():
    return {"message": "Hello World"}