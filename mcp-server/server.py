from fastapi import FastAPI
from dotenv import load_dotenv
import httpx
import os

# Database Section
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

app = FastAPI()
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database templates
class Food(Base):
    __tablename__ = "foods_cache"

    fdc_id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    calories = Column(Float)
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fat_g = Column(Float)
    brand_owner = Column(String)
    brand_name = Column(String)
    gtin_upc = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Helper Function
def extract_nutrients(food_nutrients):
    nutrients = {
        'calories': None,
        'protein_g': None,
        'carbs_g': None,
        'fat_g': None
    }

    for nutrient in food_nutrients:
        nutrient_name = nutrient.get('nutrientName', '').lower()
        value = nutrient.get('value', 0)

        if 'energy' in nutrient_name or 'calorie' in nutrient_name:
            nutrients['calories'] = value
        elif 'protein' in nutrient_name:
            nutrients['protein_g'] = value
        elif 'carbohydrate' in nutrient_name:
            nutrients['carbs_g'] = value
        elif 'fat' in nutrient_name or 'lipid' in nutrient_name:
            nutrients['fat_g'] = value
    
    return nutrients


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
    
    data = response.json()
    foods = data.get('foods', [])

    db = SessionLocal()

    try:
        for food in foods:
            fdc_id = food.get('fdcId')
            description = food.get('description', 'Unknown')
            food_nutrients = food.get('foodNutrients', [])

            existing_food = db.query(Food).filter(Food.fdc_id == fdc_id).first()

            if not existing_food:
                nutrients = extract_nutrients(food_nutrients)

                new_food = Food(
                    fdc_id = fdc_id,
                    description = description,
                    calories = nutrients['calories'],
                    protein_g = nutrients['protein_g'],
                    carbs_g = nutrients['carbs_g'],
                    fat_g = nutrients['fat_g'],
                    brand_owner = food.get('brandOwner'),
                    brand_name = food.get('brandName'),
                    gtin_upc = food.get('gtinUpc')
                )

                db.add(new_food)

        db.commit()
    
    finally:
        db.close()

    return data
