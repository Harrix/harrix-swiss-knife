"""Extract latitude and longitude from map service URLs and image EXIF."""

from __future__ import annotations

import re
from numbers import Real
from typing import TYPE_CHECKING
from urllib.parse import unquote

from PIL import Image
from PIL.ExifTags import GPS, IFD

if TYPE_CHECKING:
    from pathlib import Path

_GOOGLE_AT_PATTERN = re.compile(r"@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)")
_GOOGLE_3D4D_PATTERN = re.compile(r"!3d(-?\d+(?:\.\d+)?)!4d(-?\d+(?:\.\d+)?)")
_GOOGLE_Q_PATTERN = re.compile(r"[?&]q=(-?\d+(?:\.\d+)?)[,+](-?\d+(?:\.\d+)?)")
_YANDEX_LL_PATTERN = re.compile(r"[?&](?:ll|pt)=(-?\d+(?:\.\d+)?)[,%2C](-?\d+(?:\.\d+)?)", re.IGNORECASE)
_OSM_MAP_PATTERN = re.compile(r"#map=\d+/(-?\d+(?:\.\d+)?)/(-?\d+(?:\.\d+)?)")
_OSM_MLAT_MLON_PATTERN = re.compile(
    r"[?&]mlat=(-?\d+(?:\.\d+)?)(?:&|$).*?[?&]mlon=(-?\d+(?:\.\d+)?)|"
    r"[?&]mlon=(-?\d+(?:\.\d+)?)(?:&|$).*?[?&]mlat=(-?\d+(?:\.\d+)?)",
    re.IGNORECASE | re.DOTALL,
)
_LAT_LON_QUERY_PATTERN = re.compile(
    r"[?&]lat=(-?\d+(?:\.\d+)?)(?:&|$).*?[?&]lon=(-?\d+(?:\.\d+)?)|"
    r"[?&]lon=(-?\d+(?:\.\d+)?)(?:&|$).*?[?&]lat=(-?\d+(?:\.\d+)?)",
    re.IGNORECASE | re.DOTALL,
)
_DGIS_M_PATTERN = re.compile(r"[?&]m=(-?\d+(?:\.\d+)?)[,%2C](-?\d+(?:\.\d+)?)", re.IGNORECASE)
_COORDINATES_TEXT_PATTERN = re.compile(
    r"^\s*(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)\s*$",
)

_MAX_LATITUDE = 90
_MAX_LONGITUDE = 180
_DMS_PART_COUNT = 3
_DEFAULT_MAP_ZOOM = 17


def build_google_maps_url(lat: float, lon: float, *, zoom: int = _DEFAULT_MAP_ZOOM) -> str:
    """Return a Google Maps URL centered on the given coordinates."""
    return f"https://www.google.com/maps/@{lat},{lon},{zoom}z"


def build_openstreetmap_url(lat: float, lon: float, *, zoom: int = _DEFAULT_MAP_ZOOM) -> str:
    """Return an OpenStreetMap URL centered on the given coordinates."""
    return f"https://www.openstreetmap.org/#map={zoom}/{lat}/{lon}"


def build_yandex_maps_url(lat: float, lon: float, *, zoom: int = _DEFAULT_MAP_ZOOM) -> str:
    """Return a Yandex Maps URL centered on the given coordinates."""
    return f"https://yandex.ru/maps/?ll={lon}%2C{lat}&z={zoom}"


def extract_coordinates_from_image(path: str | Path) -> tuple[float, float] | None:
    """Return `(latitude, longitude)` from image EXIF GPS, or `None`."""
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


def extract_coordinates_from_image_paths(paths: list[str]) -> tuple[float, float] | None:
    """Return GPS from the first image path that has EXIF coordinates, or `None`."""
    for path in paths:
        coords = extract_coordinates_from_image(path)
        if coords is not None:
            return coords
    return None


def format_coordinates(lat: float, lon: float) -> str:
    """Return `lat, lon` as a human-readable pair."""
    return f"{lat:.6f}".rstrip("0").rstrip(".") + ", " + f"{lon:.6f}".rstrip("0").rstrip(".")


def parse_coordinates_from_map_url(url: str) -> tuple[float, float] | None:
    """Parse `(latitude, longitude)` from a map URL, or return `None`."""
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


def parse_coordinates_text(text: str) -> tuple[float, float] | None:
    """Parse `(latitude, longitude)` from `lat, lon` text, or return `None`."""
    match = _COORDINATES_TEXT_PATTERN.match(text.strip())
    if match is None:
        return None
    lat = float(match.group(1))
    lon = float(match.group(2))
    if not _is_valid_coordinate_pair(lat, lon):
        return None
    return lat, lon


def _as_float(value: object) -> float:
    """Convert EXIF numeric / rational values to float."""
    if isinstance(value, Real):
        return float(value)
    if isinstance(value, str):
        return float(value)
    msg = f"Cannot convert {type(value)!r} to float"
    raise TypeError(msg)


def _dms_to_decimal(dms: object, ref: str) -> float:
    """Convert EXIF degrees/minutes/seconds and hemisphere ref to a signed decimal."""
    if not isinstance(dms, (list, tuple)) or len(dms) != _DMS_PART_COUNT:
        msg = "GPS DMS must have three parts"
        raise ValueError(msg)
    degrees, minutes, seconds = (_as_float(part) for part in dms)
    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if ref.upper().startswith(("S", "W")):
        return -decimal
    return decimal


def _gps_ref_to_str(ref: object) -> str:
    if isinstance(ref, bytes):
        return ref.decode("ascii", errors="ignore")
    return str(ref)


def _is_valid_coordinate_pair(lat: float, lon: float) -> bool:
    return abs(lat) <= _MAX_LATITUDE and abs(lon) <= _MAX_LONGITUDE
