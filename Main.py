from fastapi import FastAPI, HTTPException, Query
from datetime import datetime, timezone
from fastapi.middleware.cors import CORSMiddleware
import httpx

BASE_URL = "https://api.genderize.io"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permet toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Permet toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Permet tous les headers
)


@app.get("/")
def read_root():
    return {"Hello" : "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id" : item_id, "q" : q }

@app.get("/api/classify")
async def read_gender(name: str = Query(..., min_lenght=1)):
    if (not name or not name.strip()):
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Name cannot be empty"}
        )
    
    async with httpx.AsyncClient() as client:
        response = await client.get(\
            BASE_URL,
            params={"name": name}
        )
        
        status_code = response.status_code

        if status_code in [400, 422, 500, 502]:
            raise HTTPException(
                detail: {"status":"error", "message": response.text}
            )

        gender = response.json().get("gender")
        probability = response.json().get("probability")
        sample_size = response.json().get("count")

        if gender is None or  sample_size == 0 :
            raise HTTPException(
                status_code: 404,
                detail:{"status": "error", "message": "No prediction available for the provided name"
            )
    
        is_confident = (probability>=0.7) and (sample_size>100)
        processed_at = datetime.now(timezone.utc).isoformat()
        

    return {
        "status": "success",
        "data": {
            "name": name,
            "gender": gender, 
            "probability":probability, 
            "sample_size":sample_size, 
            "is_confident": is_confident, 
            "processed_at": processed_at
        }
    }

# Pour tester CORS
@app.get("/test-cors")
async def test_cors():
    return {"message": "CORS is working!"}
