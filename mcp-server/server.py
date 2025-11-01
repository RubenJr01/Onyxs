from fastapi import FastAPI

app = FastAPI()

@app.get("/")

def read_root():
    return {"Message": "Onyxs Fitness API is running!"}

def search_food()
