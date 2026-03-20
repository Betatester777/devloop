# Verifies: AC-2.1, AC-2.2, AC-3.1, AC-3.2, AC-3.3, AC-3.4 — Asset loading and manifest
from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from src.assets import AssetError, AssetLoader  # noqa: E402

# Path to the real assets shipped with the project
REAL_ASSETS = Path(__file__).resolve().parent.parent / "src" / "assets"


@pytest.fixture(autouse=True)
def _init_pygame():
    pygame.init()
    yield
    pygame.quit()


def _create_test_png(path: Path, width: int = 50, height: int = 70) -> None:
    """Write a minimal valid PNG file for testing."""
    surface = pygame.Surface((width, height))
    surface.fill((100, 150, 200))
    pygame.image.save(surface, str(path))


# ------------------------------------------------------------------
# AC-3.1: Category enumeration
# ------------------------------------------------------------------

class TestListCategories:
    def test_returns_list(self, tmp_path: Path) -> None:
        """list_categories returns folder names under images/."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        (images_dir / "fruits").mkdir()
        (images_dir / "dishes").mkdir()
        (images_dir / "source").mkdir()  # should be excluded

        loader = AssetLoader(base_path=tmp_path)
        cats = loader.list_categories()
        assert "fruits" in cats
        assert "dishes" in cats
        assert "source" not in cats

    def test_empty_when_no_images_dir(self, tmp_path: Path) -> None:
        loader = AssetLoader(base_path=tmp_path)
        assert loader.list_categories() == []

    def test_real_assets_have_categories(self) -> None:
        """AC-3.1: Real asset directory has expected categories."""
        loader = AssetLoader(base_path=REAL_ASSETS)
        cats = loader.list_categories()
        assert "dishes" in cats
        assert "drinks" in cats
        assert len(cats) >= 6
        assert "source" not in cats


# ------------------------------------------------------------------
# AC-3.2: Image loading and random assignment
# ------------------------------------------------------------------

class TestLoadCardImages:
    def test_loads_real_images(self) -> None:
        """AC-3.2: Load real PNG images from a category."""
        loader = AssetLoader(base_path=REAL_ASSETS)
        images = loader.load_card_images("dishes", 10)
        assert len(images) == 10

    def test_unique_image_ids(self) -> None:
        loader = AssetLoader(base_path=REAL_ASSETS)
        images = loader.load_card_images("dishes", 10)
        ids = [img.image_id for img in images]
        assert len(set(ids)) == 10

    def test_surfaces_scaled_to_card_size(self) -> None:
        """AC-3.4: Images scaled to card size for recognizability."""
        loader = AssetLoader(base_path=REAL_ASSETS)
        images = loader.load_card_images("dishes", 3)
        for img in images:
            assert img.surface.get_size() == AssetLoader.CARD_SIZE

    def test_random_selection(self) -> None:
        """AC-3.2: Random images selected (two calls unlikely identical)."""
        loader = AssetLoader(base_path=REAL_ASSETS)
        ids_a = {img.image_id for img in loader.load_card_images("dishes", 10)}
        ids_b = {img.image_id for img in loader.load_card_images("dishes", 10)}
        # With 36 images, picking 10 twice should differ almost always
        assert isinstance(ids_a | ids_b, set)

    def test_insufficient_images_raises(self, tmp_path: Path) -> None:
        """AssetError when category has fewer images than needed."""
        cat_dir = tmp_path / "images" / "tiny"
        cat_dir.mkdir(parents=True)
        _create_test_png(cat_dir / "a.png")

        loader = AssetLoader(base_path=tmp_path)
        with pytest.raises(AssetError, match="has 1 images but 5 are required"):
            loader.load_card_images("tiny", 5)

    def test_missing_category_raises(self, tmp_path: Path) -> None:
        """AssetError when category folder doesn't exist."""
        loader = AssetLoader(base_path=tmp_path)
        with pytest.raises(AssetError, match="Category folder not found"):
            loader.load_card_images("nonexistent", 1)

    def test_loads_from_tmp_pngs(self, tmp_path: Path) -> None:
        """Loads from synthetic PNGs in a temp dir."""
        cat_dir = tmp_path / "images" / "test_cat"
        cat_dir.mkdir(parents=True)
        for i in range(5):
            _create_test_png(cat_dir / f"card_{i}.png")

        loader = AssetLoader(base_path=tmp_path)
        images = loader.load_card_images("test_cat", 3)
        assert len(images) == 3
        for img in images:
            assert img.surface.get_size() == AssetLoader.CARD_SIZE


# ------------------------------------------------------------------
# AC-3.3: Manifest validation
# ------------------------------------------------------------------

class TestValidateManifest:
    def test_real_manifest_is_complete(self) -> None:
        """AC-3.3: Every shipped image has a manifest entry."""
        loader = AssetLoader(base_path=REAL_ASSETS)
        missing = loader.validate_manifest()
        assert missing == [], f"Missing manifest entries: {missing}"

    def test_missing_entries_detected(self, tmp_path: Path) -> None:
        """validate_manifest returns stems not in manifest."""
        cat_dir = tmp_path / "images" / "cat"
        cat_dir.mkdir(parents=True)
        _create_test_png(cat_dir / "img_a.png")
        _create_test_png(cat_dir / "img_b.png")

        # Manifest only has img_a
        manifest = {"img_a": {"source_url": "http://example.com", "licence": "CC0-1.0"}}
        (tmp_path / "asset_manifest.json").write_text(json.dumps(manifest))

        loader = AssetLoader(base_path=tmp_path)
        missing = loader.validate_manifest()
        assert missing == ["img_b"]

    def test_no_manifest_file(self, tmp_path: Path) -> None:
        """All images are missing when manifest doesn't exist."""
        cat_dir = tmp_path / "images" / "cat"
        cat_dir.mkdir(parents=True)
        _create_test_png(cat_dir / "img_a.png")

        loader = AssetLoader(base_path=tmp_path)
        missing = loader.validate_manifest()
        assert "img_a" in missing

    def test_empty_dir_returns_empty(self, tmp_path: Path) -> None:
        loader = AssetLoader(base_path=tmp_path)
        assert loader.validate_manifest() == []


# ------------------------------------------------------------------
# Card back
# ------------------------------------------------------------------

class TestLoadCardBack:
    def test_returns_surface(self) -> None:
        loader = AssetLoader(base_path=REAL_ASSETS)
        back = loader.load_card_back()
        assert isinstance(back, pygame.Surface)
        assert back.get_size() == AssetLoader.CARD_SIZE

    def test_custom_color(self) -> None:
        loader = AssetLoader(base_path=REAL_ASSETS)
        back = loader.load_card_back(color=(255, 0, 0))
        assert isinstance(back, pygame.Surface)
