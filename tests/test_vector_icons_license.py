"""Tests for Vector Icons note license in catalog and context-menu lookup."""

from __future__ import annotations

import json
from pathlib import Path

from harrix_swiss_knife.apps.icons.catalog import (
    IconFamily,
    family_license_info,
    is_openable_license_url,
    load_catalog,
    rebuild_catalog,
)

_MIN_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><rect width="32" height="32" fill="#336699"/></svg>'
)
_LICENSE_NAME = "CC BY 4.0"
_LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"


def _write_note(repo: Path, *, license_name: str, license_url: str) -> Path:
    note = repo / "icons" / "building__house"
    note.mkdir(parents=True)
    (note / "featured-image.svg").write_text(_MIN_SVG, encoding="utf-8")
    (note / "building__house.md").write_text(
        f"---\ncategories: [building]\nlicense: {license_name}\nlicense-url: {license_url}\n---\n\n# House\n",
        encoding="utf-8",
    )
    return note


def _family(*, license_name: str = "", license_url: str = "") -> IconFamily:
    return IconFamily(
        id="building__house",
        title="House",
        categories=["building"],
        tags=[],
        folder="icons/building__house",
        featured="featured-image.svg",
        featured_hash="",
        license=license_name,
        license_url=license_url,
    )


def test_rebuild_and_load_catalog_keeps_license(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_note(repo, license_name=_LICENSE_NAME, license_url=_LICENSE_URL)
    catalog = rebuild_catalog(repo)
    family = catalog.icons[0]
    assert family.license == _LICENSE_NAME
    assert family.license_url == _LICENSE_URL

    raw = json.loads((repo / "catalog.json").read_text(encoding="utf-8"))
    assert raw["icons"][0]["license"] == _LICENSE_NAME
    assert raw["icons"][0]["license-url"] == _LICENSE_URL

    loaded = load_catalog(repo)
    assert loaded.icons[0].license == _LICENSE_NAME
    assert loaded.icons[0].license_url == _LICENSE_URL


def test_load_catalog_accepts_underscore_license_url(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "icons").mkdir(parents=True)
    (repo / "catalog.json").write_text(
        json.dumps(
            {
                "version": 1,
                "generated_at": "2026-01-01T00:00:00Z",
                "icons": [
                    {
                        "id": "building__house",
                        "title": "House",
                        "categories": ["building"],
                        "tags": [],
                        "folder": "icons/building__house",
                        "featured": "featured-image.svg",
                        "featured_hash": "",
                        "license": _LICENSE_NAME,
                        "license_url": _LICENSE_URL,
                    },
                ],
            },
        )
        + "\n",
        encoding="utf-8",
    )
    loaded = load_catalog(repo)
    assert loaded.icons[0].license == _LICENSE_NAME
    assert loaded.icons[0].license_url == _LICENSE_URL


def test_family_license_info_prefers_catalog_then_note(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_note(repo, license_name=_LICENSE_NAME, license_url=_LICENSE_URL)
    catalog_family = _family(license_name="MIT", license_url="https://opensource.org/licenses/MIT")
    assert family_license_info(catalog_family, repo) == (
        "MIT",
        "https://opensource.org/licenses/MIT",
    )

    stale = _family()
    assert family_license_info(stale, repo) == (_LICENSE_NAME, _LICENSE_URL)
    assert family_license_info(stale, None) == ("", "")


def test_is_openable_license_url() -> None:
    assert is_openable_license_url("https://creativecommons.org/licenses/by/4.0/")
    assert is_openable_license_url(" http://example.com/license ")
    assert not is_openable_license_url("")
    assert not is_openable_license_url("creativecommons.org/licenses/by/4.0/")
    assert not is_openable_license_url("file:///C:/license.txt")
    assert not is_openable_license_url("javascript:alert(1)")
