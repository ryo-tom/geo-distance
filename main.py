from fastapi import FastAPI, HTTPException, Header, Depends
from models.request import DistanceRequest
from services.geolocation import get_coordinates
from services.distance import haversine_distance, adjust_distance
from config import API_KEYS

app = FastAPI()

def verify_api_key(x_api_key: str = Header(None)) -> None:
    if not x_api_key or x_api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Authentication failed.")


@app.post("/distance", dependencies=[Depends(verify_api_key)])
def calculate_distance(request: DistanceRequest):
    coord1 = get_coordinates(request.address1)
    coord2 = get_coordinates(request.address2)

    if not coord1:
        raise HTTPException(status_code=400, detail=f"住所 '{request.address1}' の座標を取得できません")
    if not coord2:
        raise HTTPException(status_code=400, detail=f"住所 '{request.address2}' の座標を取得できません")

    distance = haversine_distance(coord1, coord2)
    adjusted = adjust_distance(distance)

    return {
        "distance": adjusted
    }