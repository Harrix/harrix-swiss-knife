"""Tests for map URL coordinate extraction."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from PIL.ExifTags import GPS, IFD

from harrix_swiss_knife.map_coordinates import (
    build_google_maps_url,
    build_openstreetmap_url,
    build_yandex_maps_url,
    extract_coordinates_from_image,
    extract_coordinates_from_image_paths,
    format_coordinates,
    parse_coordinates_from_map_url,
    parse_coordinates_text,
)


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


def test_parse_coordinates_text() -> None:
    assert parse_coordinates_text("55.7558, 37.6173") == (55.7558, 37.6173)
    assert parse_coordinates_text("55.7558;37.6173") == (55.7558, 37.6173)
    assert parse_coordinates_text("not coordinates") is None


def test_build_map_urls() -> None:
    assert build_google_maps_url(55.7558, 37.6173) == "https://www.google.com/maps?q=55.7558,37.6173"
    assert build_yandex_maps_url(55.7558, 37.6173) == (
        "https://yandex.ru/maps/?ll=37.6173%2C55.7558&pt=37.6173,55.7558&z=17"
    )
    assert build_openstreetmap_url(55.7558, 37.6173) == (
        "https://www.openstreetmap.org/?mlat=55.7558&mlon=37.6173#map=17/55.7558/37.6173"
    )


def test_extract_coordinates_from_image_exif(tmp_path: Path) -> None:
    path = tmp_path / "with-gps.jpg"
    image = Image.new("RGB", (20, 20), color=(255, 0, 0))
    exif = Image.Exif()
    exif[IFD.GPSInfo] = {
        GPS.GPSLatitudeRef: "N",
        GPS.GPSLatitude: (55.0, 45.0, 20.9736),
        GPS.GPSLongitudeRef: "E",
        GPS.GPSLongitude: (37.0, 37.0, 2.27964),
    }
    image.save(path, exif=exif, format="JPEG")

    result = extract_coordinates_from_image(path)
    assert result is not None
    assert abs(result[0] - 55.755826) < 1e-5
    assert abs(result[1] - 37.6173) < 1e-4


def test_extract_coordinates_from_image_without_gps(tmp_path: Path) -> None:
    path = tmp_path / "no-gps.jpg"
    Image.new("RGB", (20, 20), color=(0, 255, 0)).save(path, format="JPEG")
    assert extract_coordinates_from_image(path) is None


def test_extract_coordinates_from_image_paths_uses_first_with_gps(tmp_path: Path) -> None:
    no_gps = tmp_path / "no-gps.jpg"
    with_gps = tmp_path / "with-gps.jpg"
    Image.new("RGB", (20, 20), color=(0, 0, 255)).save(no_gps, format="JPEG")

    image = Image.new("RGB", (20, 20), color=(255, 0, 0))
    exif = Image.Exif()
    exif[IFD.GPSInfo] = {
        GPS.GPSLatitudeRef: "S",
        GPS.GPSLatitude: (33.0, 52.0, 0.0),
        GPS.GPSLongitudeRef: "W",
        GPS.GPSLongitude: (151.0, 12.0, 0.0),
    }
    image.save(with_gps, exif=exif, format="JPEG")

    result = extract_coordinates_from_image_paths([str(no_gps), str(with_gps)])
    assert result is not None
    assert abs(result[0] - (-33.8666667)) < 1e-5
    assert abs(result[1] - (-151.2)) < 1e-5
