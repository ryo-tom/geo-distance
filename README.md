# geo-distance

2点間の住所から経路距離を取得するAPI。

ref:

- <https://geopy.readthedocs.io/en/stable/>

## APIの確認

試しに「ディズニーランド」から「USJ」までの距離を求めてみる。

```bash
curl -X 'POST' 'http://127.0.0.1:8000/distance' \
-H 'Content-Type: application/json' \
-d '{"address1": "千葉県浦安市舞浜１−１", "address2": "大阪府大阪市此花区桜島２丁目１−３３"}'
```

レスポンス:

```bash
{"address1":"〒279-0031 千葉県浦安市舞浜１−１","address2":"大阪府大阪市","coord1":[35.6530518,139.9018495],"coord2":[34.6937569,135.5014539],"haversine_distance_km":413.9,"adjusted_distance_km":538.07}
```

取得距離: 538km
GoogleMap: 523km
・・・誤差の範囲！

海を挟んで直線距離では近いけど、車では迂回しないといけない2点間（例えば、中部国際空港と伊勢神宮）だとどうしても誤差が大きくなる。

```bash
curl -X 'POST' 'http://127.0.0.1:8000/distance' \
-H 'Content-Type: application/json' \
-d '{"address1": "愛知県常滑市セントレア１丁目１番地", "address2": "三重県伊勢市宇治館町１"}'
```

取得距離: 58km
GoogleMap: 160km
