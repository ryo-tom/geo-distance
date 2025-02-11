from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import re


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


def get_coordinates(address: str) -> tuple:
    """住所を座標に変換する（段階的に簡略化しながら検索）"""
    geolocator = Nominatim(user_agent="geoapi")
    addresses = build_address_variations(address)

    for address in addresses:
        location = retry_geocode(geolocator, address)
        if location:
            print(f"住所 '{address}' で座標を取得しました: ({location.latitude}, {location.longitude})")
            return location.latitude, location.longitude

    print(f"住所 '{address}' の座標を最終的に取得できませんでした")
    return None


def build_address_variations(address: str) -> list:
    """番地まで指定された住所を、より広い範囲の住所に変換（lazy → greedy → prefecture）"""
    variations = [address]

    municipality_lazy = extract_municipality_lazy(address)
    municipality_greedy = extract_municipality_greedy(address)
    prefecture = extract_prefecture(address)

    if municipality_lazy and municipality_lazy != address:
        variations.append(municipality_lazy)

    if municipality_greedy and municipality_greedy != address and municipality_greedy not in variations:
        variations.append(municipality_greedy)

    if prefecture and prefecture not in variations:
        variations.append(prefecture)

    return variations


def retry_geocode(geolocator, address: str, retries=1, delay=2) -> tuple:
    """Nominatim API のタイムアウト時にリトライする"""
    for attempt in range(retries + 1):
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                return location
            else:
                print(f"住所 '{address}' では座標が見つかりません。")
        except GeocoderTimedOut:
            print(f"住所 '{address}' の座標取得がタイムアウトしました。リトライ中... ({attempt + 1}/{retries})")
            time.sleep(delay)

    return None
