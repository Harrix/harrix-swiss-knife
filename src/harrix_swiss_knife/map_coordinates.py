"""Extract latitude and longitude from map service URLs."""

from __future__ import annotations

import re
from urllib.parse import unquote

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

_MAX_LATITUDE = 90
_MAX_LONGITUDE = 180


def format_coordinates(lat: float, lon: float) -> str:
    """Return ``lat, lon`` as a human-readable pair."""
    return f"{lat:.6f}".rstrip("0").rstrip(".") + ", " + f"{lon:.6f}".rstrip("0").rstrip(".")


def parse_coordinates_from_map_url(url: str) -> tuple[float, float] | None:
    """Parse ``(latitude, longitude)`` from a map URL, or return ``None``."""
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


def _is_valid_coordinate_pair(lat: float, lon: float) -> bool:
    return abs(lat) <= _MAX_LATITUDE and abs(lon) <= _MAX_LONGITUDE
