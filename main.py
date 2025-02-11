from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from math import radians, sin, cos, sqrt, atan2
import time
import re


app = FastAPI()

class DistanceRequest(BaseModel):
    address1: str
    address2: str


def extract_municipality_lazy(address: str) -> str:
    """市区町村・郡レベルの住所を最短一致（lazy）で抽出"""
    match = re.search(r"^(.*?(市|区|町|村|群))", address)
    return match.group(1) if match else None


def extract_municipality_greedy(address: str) -> str:
    """市区町村・郡レベルの住所を貪欲一致（greedy）で抽出"""
    match = re.search(r"^(.*(市|区|町|村|群))", address)
    return match.group(1) if match else None


def extract_prefecture(address: str) -> str:
    """都道府県名を正規表現で抽出"""
    match = re.search(r"(東京都|北海道|大阪府|京都府|.{2,3}県)", address)
    return match.group(1) if match else None


def get_coordinates(address):
    """住所を座標に変換する（段階的に絞り込む）"""
    geolocator = Nominatim(user_agent="geoapi")
    retry_count = 1

    addresses = [address]
    municipality = extract_municipality_lazy(address)
    municipality_greedy = extract_municipality_greedy(address)
    if municipality and municipality != address:
        addresses.append(municipality)
    if municipality_greedy and municipality_greedy != address:
        addresses.append(municipality_greedy)

    prefecture = extract_prefecture(address)
    if prefecture and prefecture != address and prefecture != municipality and prefecture != municipality_greedy:
        addresses.append(prefecture)

    for address in addresses:
        for attempt in range(retry_count + 1):
            try:
                location = geolocator.geocode(address, timeout=10)
                if location:
                    print(f"住所 '{address} で座標を取得。")
                    return (location.latitude, location.longitude)
                else:
                    print(f"住所 '{address} では座標が見つかりません。")
            except GeocoderTimedOut:
                print(f"住所 '{address}' の座標取得がタイムアウトしました。リトライ中...")
                time.sleep(2)
                continue

    print(f"住所 '{address}' の座標が最終的に見つかりませんでした")
    return None


def haversine_distance(coord1, coord2):
    """ 2点間のハーバーサイン距離を計算 """
    R = 6371.01  # 地球の平均半径 (km)
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c  # km単位の距離


def adjust_distance(distance):
    """道路の迂回を考慮して1.3倍に補正"""
    factor = 1.3  # 都市部なら1.2、地方なら1.3～1.5を調整
    return distance * factor


@app.post("/distance")
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
        "address1": request.address1,
        "address2": request.address2,
        "coord1": coord1,
        "coord2": coord2,
        "haversine_distance_km": round(distance, 2),
        "adjusted_distance_km": round(adjusted, 2)
    }