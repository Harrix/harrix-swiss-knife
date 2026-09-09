"""Tests for icon family-id derivation from variant stems."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.apps.icons.add_vector import merge_variant_dest_name
from harrix_swiss_knife.apps.icons.add_vector_meta import defaults_from_source_stem
from harrix_swiss_knife.apps.icons.family_id import family_id_from_stem, title_from_family_id


def test_family_id_from_stem_strips_color_and_line_variants() -> None:
    assert family_id_from_stem("building__garage_black") == "building__garage"
    assert family_id_from_stem("human__bone_improbable_black_line-8") == "human__bone"
    assert family_id_from_stem("human__bone_improbable_black-line-8") == "human__bone"
    assert family_id_from_stem("human__bone_improbable_white-line-8") == "human__bone"
    assert family_id_from_stem("it__grid_black_line-16-") == "it__grid"
    assert family_id_from_stem("it__grid_white_line-16-") == "it__grid"
    assert family_id_from_stem("human__bone_graysvg") == "human__bone"
    assert family_id_from_stem("object__extinguisher_graysvg") == "object__extinguisher"
    assert family_id_from_stem("object__extinguisher_gray") == "object__extinguisher"


def test_title_from_family_id_after_glued_svg() -> None:
    family_id = family_id_from_stem("human__bone_graysvg")
    assert family_id == "human__bone"
    assert title_from_family_id(family_id) == "Bone"


def test_defaults_from_source_stem_hyphen_and_graysvg() -> None:
    family_id, title, category = defaults_from_source_stem("human__bone_improbable_black-line-8")
    assert family_id == "human__bone"
    assert title == "Bone"
    assert category == "human"

    family_id, title, category = defaults_from_source_stem("object__extinguisher_graysvg")
    assert family_id == "object__extinguisher"
    assert title == "Extinguisher"
    assert category == "object"


def test_merge_variant_dest_name_renames_graysvg() -> None:
    assert merge_variant_dest_name(Path("human__bone_graysvg.svg"), family_id="human__bone") == "human__bone_gray.svg"
    assert (
        merge_variant_dest_name(
            Path("human__bone_improbable_black-line-8.svg"),
            family_id="human__bone",
        )
        == "human__bone_improbable_black-line-8.svg"
    )


def test_merge_variant_dest_name_strips_trailing_line_hyphen() -> None:
    assert (
        merge_variant_dest_name(
            Path("it__grid_black_line-16-.svg"),
            family_id="it__grid",
        )
        == "it__grid_black_line-16.svg"
    )
    assert (
        merge_variant_dest_name(
            Path("it__grid_white_line-16-.svg"),
            family_id="it__grid",
        )
        == "it__grid_white_line-16.svg"
    )
