from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

api_url = "https://api.genderize.io"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.get('/')
def root():
    return {"app":"Racine"}

@app.get('/api/classify')
async def get_gender(name : str):
    if not name or not name.strip:
        message = "Bad Request"
        raise HTTPException(
            status_code=400,
            detail={ "status": "error", "message": message }
        )
    

    async with httpx.AsyncClient() as client:
        response = await client.get(
            api_url,
            params={"name":name}
        )
        data = response.json()

        gender = data.get("gender")
        sample_size = data.get("count")

        if gender is None or sample_size==0:
            print(f"genre vaut {gender}")
            return { "status": "error", "message": "No prediction available for the provided name" }
        
        probability = data.get("probability")
        is_confident = probability >= 0.7 and sample_size >= 100
        processed_at = datetime.now(timezone.utc).isoformat(timespec='seconds').replace("+00:00", "Z")

    return {
        "status":"success",
        "data":{
            "name":name,
            "gende":gender,
            "probability":probability,
            "sample_size":sample_size,
            "is_confident":is_confident,
            "processed_at":processed_at
        }
    }
