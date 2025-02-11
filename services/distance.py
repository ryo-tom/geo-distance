from math import radians, sin, cos, sqrt, atan2


def haversine_distance(coord1: tuple, coord2: tuple) -> int:
    """2点間のハーバーサイン距離を計算"""
    R = 6371.01  # 地球の平均半径 (km)
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return int(R * c)


def adjust_distance(distance: float) -> int:
    """道路の迂回を考慮して1.3倍に補正"""
    factor = 1.3
    return int(distance * factor)


