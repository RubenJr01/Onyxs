from fastapi import FastAPI
from dotenv import load_dotenv
import httpx
import os

app = FastAPI()
load_dotenv()

@app.get("/")
def read_root():
    return {"Message": "Onyxs Fitness API is running!"}

@app.post("/search_food")
async def search_food(query: str, limit: int = 15):
    API_KEY = os.getenv("USDA_API_KEY")
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params= {
            "api_key": API_KEY,
            "query": query,
            "pageSize": limit
        })
    return response.json()
