---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `map_coordinates.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `format_coordinates`](#-function-format_coordinates)
- [🔧 Function `parse_coordinates_from_map_url`](#-function-parse_coordinates_from_map_url)
- [🔧 Function `_is_valid_coordinate_pair`](#-function-_is_valid_coordinate_pair)

</details>

## 🔧 Function `format_coordinates`

```python
def format_coordinates(lat: float, lon: float) -> str
```

Return `lat, lon` as a human-readable pair.

<details>
<summary>Code:</summary>

```python
def format_coordinates(lat: float, lon: float) -> str:
    return f"{lat:.6f}".rstrip("0").rstrip(".") + ", " + f"{lon:.6f}".rstrip("0").rstrip(".")
```

</details>

## 🔧 Function `parse_coordinates_from_map_url`

```python
def parse_coordinates_from_map_url(url: str) -> tuple[float, float] | None
```

Parse `(latitude, longitude)` from a map URL, or return `None`.

<details>
<summary>Code:</summary>

```python
def parse_coordinates_from_map_url(url: str) -> tuple[float, float] | None:
    text = unquote(url.strip())
    if not text:
        return None

    parsers: list[tuple[str, re.Pattern[str], bool]] = [
        ("google_3d4d", _GOOGLE_3D4D_PATTERN, False),
        ("google_at", _GOOGLE_AT_PATTERN, False),
        ("google_q", _GOOGLE_Q_PATTERN, False),
        ("yandex_ll", _YANDEX_LL_PATTERN, True),
        ("dgis_m", _DGIS_M_PATTERN, True),
        ("osm_map", _OSM_MAP_PATTERN, False),
    ]

    for _name, pattern, lon_lat_order in parsers:
        match = pattern.search(text)
        if match is None:
            continue
        first = float(match.group(1))
        second = float(match.group(2))
        if lon_lat_order:
            lat, lon = second, first
        else:
            lat, lon = first, second
        if _is_valid_coordinate_pair(lat, lon):
            return lat, lon

    mlat_mlon = _OSM_MLAT_MLON_PATTERN.search(text)
    if mlat_mlon is not None:
        if mlat_mlon.group(1) is not None and mlat_mlon.group(2) is not None:
            lat = float(mlat_mlon.group(1))
            lon = float(mlat_mlon.group(2))
        else:
            lat = float(mlat_mlon.group(4))  # type: ignore[arg-type]
            lon = float(mlat_mlon.group(3))  # type: ignore[arg-type]
        if _is_valid_coordinate_pair(lat, lon):
            return lat, lon

    lat_lon = _LAT_LON_QUERY_PATTERN.search(text)
    if lat_lon is not None:
        if lat_lon.group(1) is not None and lat_lon.group(2) is not None:
            lat = float(lat_lon.group(1))
            lon = float(lat_lon.group(2))
        else:
            lat = float(lat_lon.group(4))  # type: ignore[arg-type]
            lon = float(lat_lon.group(3))  # type: ignore[arg-type]
        if _is_valid_coordinate_pair(lat, lon):
            return lat, lon

    return None
```

</details>

## 🔧 Function `_is_valid_coordinate_pair`

```python
def _is_valid_coordinate_pair(lat: float, lon: float) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_valid_coordinate_pair(lat: float, lon: float) -> bool:
    return abs(lat) <= _MAX_LATITUDE and abs(lon) <= _MAX_LONGITUDE
```

</details>
