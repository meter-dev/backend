# Meter-Crawler

This tool can crawl the websites and generate a formatted report (JSON).

## Supported website

- https://scweb.cwb.gov.tw/
- https://fhy.wra.gov.tw/
- https://www.taipower.com.tw/

## Earthquake

- https://scweb.cwb.gov.tw/zh-tw/earthquake/data

### query parameters

- year
- month

### report

```json
[
  {
    "timestamp": <str>,
    "geometry": {
      "type": "Point",
      "coordinates": [ <float>, <float> ]
    },
    "scale": <float>,
    "intensity": [ <int>, <int>, <int> ],
    "link": <str>,
    "img": <str>
  },
  ...
]
```

example : [eq.json](/crawler/example/eq.json)

- coordinates : ( 經度, 緯度 )
- scale : 規模
- intensity : 震度 ( 竹, 中, 南 )

## Reservoir

- https://fhy.wra.gov.tw/ReservoirPage_2011/Statistics.aspx

### query parameters

- year
- month
- day

### report

```json
[
  {
    "name": <str>,
    "timestamp": <int>,
    "storage": <float>,
    "percent": <float>
  },
  ...
]
```

example : [dam.json](/crawler/example/dam.json)

- storage : 有效蓄水量 ( 萬立方公尺 )
- percent : 蓄水百分比 ( % )

## Power

- https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/loadareas.csv
- https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/loadpara.json

### query parameters

- (none) 只可查詢當日的資料

### report

```json
[
  {
    "timestamp": <int>,
    "east": {
      "load": <float>,
      "max_supply": <float>,
      "recv_rate": <float>
    },
    "south": { ... },
    "central": { ... },
    "north": { ... }
  },
  ...
]
```

example : [power.json](/crawler/example/power.json)

- load : 區域用電量 ( 萬瓩 )
- max_supply : 區域最大供電能力 ( 萬瓩 )
- recv_rate : 區域備轉容量率 ( % )
