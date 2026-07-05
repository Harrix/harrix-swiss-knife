"""Tests for map URL coordinate extraction."""

from __future__ import annotations

from harrix_swiss_knife.map_coordinates import format_coordinates, parse_coordinates_from_map_url


def test_google_maps_at_coordinates() -> None:
    url = "https://www.google.com/maps/place/Coffee/@55.755826,37.6172999,17z"
    result = parse_coordinates_from_map_url(url)
    assert result is not None
    assert abs(result[0] - 55.755826) < 1e-5
    assert abs(result[1] - 37.6172999) < 1e-5


def test_google_maps_3d4d_coordinates() -> None:
    url = "https://www.google.com/maps/place/test/data=!3d55.755826!4d37.6172999"
    result = parse_coordinates_from_map_url(url)
    assert result is not None
    assert abs(result[0] - 55.755826) < 1e-5
    assert abs(result[1] - 37.6172999) < 1e-5


def test_yandex_maps_ll_coordinates() -> None:
    url = "https://yandex.ru/maps/?ll=37.617299%2C55.755826&z=16"
    result = parse_coordinates_from_map_url(url)
    assert result is not None
    assert abs(result[0] - 55.755826) < 1e-5
    assert abs(result[1] - 37.617299) < 1e-5


def test_openstreetmap_hash_coordinates() -> None:
    url = "https://www.openstreetmap.org/#map=17/55.7558/37.6173"
    result = parse_coordinates_from_map_url(url)
    assert result is not None
    assert abs(result[0] - 55.7558) < 1e-4
    assert abs(result[1] - 37.6173) < 1e-4


def test_openstreetmap_mlat_mlon_coordinates() -> None:
    url = "https://www.openstreetmap.org/?mlat=55.7558&mlon=37.6173#map=17/55.7558/37.6173"
    result = parse_coordinates_from_map_url(url)
    assert result is not None
    assert abs(result[0] - 55.7558) < 1e-4


def test_format_coordinates_trims_trailing_zeros() -> None:
    assert format_coordinates(55.755826, 37.6173) == "55.755826, 37.6173"
