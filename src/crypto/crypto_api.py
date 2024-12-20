from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crypto_statistics import get_crypto_stats

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend running on port 3000
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

class CryptoStatsRequest(BaseModel):
    selected_crypto_symbol: str
    period: int

@app.post("/get_crypto_stats")
async def get_crypto_stats_endpoint(request: CryptoStatsRequest):
    try:
        stats = get_crypto_stats(request.selected_crypto_symbol, request.period)
        if 'error' in stats:
            raise HTTPException(status_code=400, detail=stats['error'])
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Crypto API is running!"}