"""Tests for xrf.comparison.category_registry.Category_Registry."""

import json
import logging
from pathlib import Path

import pytest

from xrf.config import Xrf_Comparison_Config
from xrf.comparison.category_registry import Category_Registry


def test_validate_category_tag_accepts_allowed_tag():
    Config = Xrf_Comparison_Config()
    Category_Registry.Validate_Category_Tag("illustration", Config)


def test_validate_category_tag_rejects_unknown_tag():
    Config = Xrf_Comparison_Config()
    with pytest.raises(ValueError):
        Category_Registry.Validate_Category_Tag("not_a_real_category", Config)


def test_write_and_load_page_category_round_trip(Temp_Meta_Path: Path):
    Config = Xrf_Comparison_Config()
    Category_Registry.Write_Page_Category(
        Temp_Meta_Path,
        "illustration",
        Config,
        Tag_Source="manual",
        Secondary_Categories=["chapter_start"],
        Notes="Full-page miniature",
    )

    Metadata = json.loads(Temp_Meta_Path.read_text(encoding="utf-8"))
    assert Metadata["optimal_k"] == 8
    assert Metadata["structural_category"] == "illustration"
    assert Metadata["structural_category_source"] == "manual"
    assert Metadata["structural_category_secondary"] == ["chapter_start"]
    assert Metadata["structural_category_notes"] == "Full-page miniature"

    assert Category_Registry.Load_Page_Category(Temp_Meta_Path) == "illustration"


def test_write_page_category_rejects_invalid_category(Temp_Meta_Path: Path):
    Config = Xrf_Comparison_Config()
    with pytest.raises(ValueError):
        Category_Registry.Write_Page_Category(Temp_Meta_Path, "bogus", Config)


def test_load_page_category_returns_none_when_untagged(Temp_Meta_Path: Path):
    assert Category_Registry.Load_Page_Category(Temp_Meta_Path) is None


def test_load_page_category_raises_on_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        Category_Registry.Load_Page_Category(tmp_path / "does_not_exist_meta.json")


def test_list_tagged_pages_groups_by_category(tmp_path: Path):
    Config = Xrf_Comparison_Config()

    Page_001 = tmp_path / "page_001_meta.json"
    Page_001.write_text(json.dumps({"optimal_k": 8}), encoding="utf-8")
    Category_Registry.Write_Page_Category(Page_001, "text_only", Config)

    Page_002 = tmp_path / "page_002_meta.json"
    Page_002.write_text(json.dumps({"optimal_k": 6}), encoding="utf-8")
    Category_Registry.Write_Page_Category(Page_002, "illustration", Config)

    Page_003 = tmp_path / "page_003_meta.json"
    Page_003.write_text(json.dumps({"optimal_k": 5}), encoding="utf-8")

    Grouped = Category_Registry.List_Tagged_Pages(tmp_path, Config)

    assert Grouped["text_only"] == ["page_001"]
    assert Grouped["illustration"] == ["page_002"]
    assert Grouped["untagged"] == ["page_003"]


def test_list_tagged_pages_warns_on_unknown_tag(tmp_path: Path, caplog):
    Config = Xrf_Comparison_Config()

    Page_001 = tmp_path / "page_001_meta.json"
    Page_001.write_text(
        json.dumps({"optimal_k": 8, "structural_category": "not_in_vocab"}),
        encoding="utf-8",
    )

    with caplog.at_level(logging.WARNING):
        Grouped = Category_Registry.List_Tagged_Pages(tmp_path, Config)

    assert Grouped["not_in_vocab"] == ["page_001"]
    assert any("unexpected category" in Record.message for Record in caplog.records)
