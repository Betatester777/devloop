# Verifies: AC-2.1, AC-2.2, AC-2.3, AC-2.4 — Asset loading and manifest validation
# Requirement: REQ-2 (Food-themed content categories)

from __future__ import annotations

import os

import pygame
import pytest

# Ensure headless mode for CI
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from src.assets.loader import AssetLoader  # noqa: E402

EXPECTED_CATEGORIES = [
    "cooking_devices",
    "dishes",
    "drinks",
    "easter_eggs",
    "finger_food",
    "kitchen_utensils",
]


@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    """Initialise pygame once for the module (needed for image loading)."""
    pygame.init()
    # Create a tiny display surface so convert_alpha works
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


@pytest.fixture()
def loader():
    return AssetLoader()


# --- AC-2.1: Category discovery ---


class TestCategories:
    def test_returns_sorted_list(self, loader: AssetLoader):
        cats = loader.categories()
        assert cats == sorted(cats)

    def test_matches_expected_subfolders(self, loader: AssetLoader):
        assert loader.categories() == EXPECTED_CATEGORIES

    def test_excludes_source_directory(self, loader: AssetLoader):
        assert "source" not in loader.categories()


# --- AC-2.1: Image ID discovery ---


class TestImageIds:
    def test_returns_36_ids_per_category(self, loader: AssetLoader):
        for cat in EXPECTED_CATEGORIES:
            ids = loader.image_ids(cat)
            assert len(ids) == 36, f"{cat} has {len(ids)} images, expected 36"

    def test_ids_are_sorted(self, loader: AssetLoader):
        for cat in EXPECTED_CATEGORIES:
            ids = loader.image_ids(cat)
            assert ids == sorted(ids)

    def test_nonexistent_category_raises(self, loader: AssetLoader):
        with pytest.raises(FileNotFoundError):
            loader.image_ids("nonexistent_category")


# --- AC-2.3: Image loading ---


class TestGetImage:
    def test_returns_surface(self, loader: AssetLoader):
        cat = EXPECTED_CATEGORIES[0]
        image_id = loader.image_ids(cat)[0]
        surface = loader.get_image(cat, image_id)
        assert isinstance(surface, pygame.Surface)

    def test_surface_size_333x333(self, loader: AssetLoader):
        cat = EXPECTED_CATEGORIES[0]
        image_id = loader.image_ids(cat)[0]
        surface = loader.get_image(cat, image_id)
        assert surface.get_size() == (333, 333)

    def test_caches_surface(self, loader: AssetLoader):
        cat = EXPECTED_CATEGORIES[0]
        image_id = loader.image_ids(cat)[0]
        s1 = loader.get_image(cat, image_id)
        s2 = loader.get_image(cat, image_id)
        assert s1 is s2

    def test_nonexistent_image_raises(self, loader: AssetLoader):
        with pytest.raises(FileNotFoundError):
            loader.get_image(EXPECTED_CATEGORIES[0], "no_such_image")


class TestGetImageScaled:
    def test_scaled_to_requested_size(self, loader: AssetLoader):
        cat = EXPECTED_CATEGORIES[0]
        image_id = loader.image_ids(cat)[0]
        surface = loader.get_image_scaled(cat, image_id, (100, 100))
        assert surface.get_size() == (100, 100)

    def test_caches_by_size(self, loader: AssetLoader):
        cat = EXPECTED_CATEGORIES[0]
        image_id = loader.image_ids(cat)[0]
        s1 = loader.get_image_scaled(cat, image_id, (100, 100))
        s2 = loader.get_image_scaled(cat, image_id, (100, 100))
        assert s1 is s2


# --- AC-2.2: Random pair sampling ---


class TestSamplePairs:
    def test_returns_2n_items(self, loader: AssetLoader):
        cat = EXPECTED_CATEGORIES[0]
        pairs = loader.sample_pairs(cat, 3)
        assert len(pairs) == 6

    def test_each_id_appears_exactly_twice(self, loader: AssetLoader):
        cat = EXPECTED_CATEGORIES[0]
        pairs = loader.sample_pairs(cat, 5)
        from collections import Counter

        counts = Counter(pairs)
        assert all(c == 2 for c in counts.values())
        assert len(counts) == 5

    def test_drawn_from_category(self, loader: AssetLoader):
        cat = EXPECTED_CATEGORIES[0]
        valid_ids = set(loader.image_ids(cat))
        pairs = loader.sample_pairs(cat, 4)
        assert all(p in valid_ids for p in pairs)

    def test_raises_if_n_exceeds_images(self, loader: AssetLoader):
        cat = EXPECTED_CATEGORIES[0]
        with pytest.raises(ValueError, match="only 36 images"):
            loader.sample_pairs(cat, 100)


    def test_n_zero_returns_empty_list(self, loader: AssetLoader):
        cat = EXPECTED_CATEGORIES[0]
        assert loader.sample_pairs(cat, 0) == []

    def test_successive_calls_produce_different_orderings(self, loader: AssetLoader):
        """Verify sample_pairs shuffles output — identical orderings across many calls
        would indicate no randomisation (probability of all-same is negligible)."""
        cat = EXPECTED_CATEGORIES[0]
        results = [tuple(loader.sample_pairs(cat, 4)) for _ in range(30)]
        assert len(set(results)) > 1, "sample_pairs returned identical ordering every time"


# --- AC-2.4: Manifest validation ---


class TestValidateManifest:
    def test_shipped_manifest_valid(self, loader: AssetLoader):
        violations = loader.validate_manifest()
        assert violations == [], f"Manifest violations: {violations}"

    def test_all_216_images_covered(self, loader: AssetLoader):
        """Ensure manifest has entries for every discovered image."""
        total = sum(len(loader.image_ids(c)) for c in loader.categories())
        assert total == 216
        # And no violations
        assert loader.validate_manifest() == []

    def test_licence_identifiers_match_spdx_format(self, loader: AssetLoader):
        """Every licence field must look like a valid SPDX identifier
        (alphanumeric, hyphens, dots, plus) — not an empty placeholder."""
        import json
        import re
        from pathlib import Path

        manifest_path = Path("src/assets/asset_manifest.json")
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        spdx_pattern = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-.+]*$")
        invalid = [
            image_id
            for image_id, entry in manifest.items()
            if not spdx_pattern.match(entry.get("licence", ""))
        ]
        assert invalid == [], f"Non-SPDX licence identifiers found: {invalid}"
