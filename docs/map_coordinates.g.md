---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `map_coordinates.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_google_maps_url`](#-function-build_google_maps_url)
- [🔧 Function `build_openstreetmap_url`](#-function-build_openstreetmap_url)
- [🔧 Function `build_yandex_maps_url`](#-function-build_yandex_maps_url)
- [🔧 Function `extract_coordinates_from_image`](#-function-extract_coordinates_from_image)
- [🔧 Function `extract_coordinates_from_image_paths`](#-function-extract_coordinates_from_image_paths)
- [🔧 Function `format_coordinates`](#-function-format_coordinates)
- [🔧 Function `parse_coordinates_from_map_url`](#-function-parse_coordinates_from_map_url)
- [🔧 Function `parse_coordinates_text`](#-function-parse_coordinates_text)

</details>

## 🔧 Function `build_google_maps_url`

```python
def build_google_maps_url(lat: float, lon: float) -> str
```

Return a Google Maps URL centered on the given coordinates.

<details>
<summary>Code:</summary>

```python
def build_google_maps_url(lat: float, lon: float, *, zoom: int = _DEFAULT_MAP_ZOOM) -> str:
    return f"https://www.google.com/maps/@{lat},{lon},{zoom}z"
```

</details>

## 🔧 Function `build_openstreetmap_url`

```python
def build_openstreetmap_url(lat: float, lon: float) -> str
```

Return an OpenStreetMap URL centered on the given coordinates.

<details>
<summary>Code:</summary>

```python
def build_openstreetmap_url(lat: float, lon: float, *, zoom: int = _DEFAULT_MAP_ZOOM) -> str:
    return f"https://www.openstreetmap.org/#map={zoom}/{lat}/{lon}"
```

</details>

## 🔧 Function `build_yandex_maps_url`

```python
def build_yandex_maps_url(lat: float, lon: float) -> str
```

Return a Yandex Maps URL centered on the given coordinates.

<details>
<summary>Code:</summary>

```python
def build_yandex_maps_url(lat: float, lon: float, *, zoom: int = _DEFAULT_MAP_ZOOM) -> str:
    return f"https://yandex.ru/maps/?ll={lon}%2C{lat}&z={zoom}"
```

</details>

## 🔧 Function `extract_coordinates_from_image`

```python
def extract_coordinates_from_image(path: str | Path) -> tuple[float, float] | None
```

Return `(latitude, longitude)` from image EXIF GPS, or `None`.

<details>
<summary>Code:</summary>

```python
def extract_coordinates_from_image(path: str | Path) -> tuple[float, float] | None:
    try:
        with Image.open(path) as image:
            exif = image.getexif()
            if not exif:
                return None
            gps_info = exif.get_ifd(IFD.GPSInfo)
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return None

    if not gps_info:
        return None

    lat_values = gps_info.get(GPS.GPSLatitude)
    lat_ref = gps_info.get(GPS.GPSLatitudeRef)
    lon_values = gps_info.get(GPS.GPSLongitude)
    lon_ref = gps_info.get(GPS.GPSLongitudeRef)
    if lat_values is None or lon_values is None or lat_ref is None or lon_ref is None:
        return None

    try:
        lat = _dms_to_decimal(lat_values, _gps_ref_to_str(lat_ref))
        lon = _dms_to_decimal(lon_values, _gps_ref_to_str(lon_ref))
    except (TypeError, ValueError, ZeroDivisionError):
        return None

    if not _is_valid_coordinate_pair(lat, lon):
        return None
    return lat, lon
```

</details>

## 🔧 Function `extract_coordinates_from_image_paths`

```python
def extract_coordinates_from_image_paths(paths: list[str]) -> tuple[float, float] | None
```

Return GPS from the first image path that has EXIF coordinates, or `None`.

<details>
<summary>Code:</summary>

```python
def extract_coordinates_from_image_paths(paths: list[str]) -> tuple[float, float] | None:
    for path in paths:
        coords = extract_coordinates_from_image(path)
        if coords is not None:
            return coords
    return None
```

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

## 🔧 Function `parse_coordinates_text`

```python
def parse_coordinates_text(text: str) -> tuple[float, float] | None
```

Parse `(latitude, longitude)` from `lat, lon` text, or return `None`.

<details>
<summary>Code:</summary>

```python
def parse_coordinates_text(text: str) -> tuple[float, float] | None:
    match = _COORDINATES_TEXT_PATTERN.match(text.strip())
    if match is None:
        return None
    lat = float(match.group(1))
    lon = float(match.group(2))
    if not _is_valid_coordinate_pair(lat, lon):
        return None
    return lat, lon
```

</details>
