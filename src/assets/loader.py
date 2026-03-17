# Implements: REQ-2 AC-2.1, AC-2.2, AC-2.3, AC-2.4 — Asset loading and manifest validation
# See: ARC §src/assets/loader.py, TD-7

from __future__ import annotations

import json
import random
from pathlib import Path

import pygame

# Categories in source/ are sprite sheets, not playable categories.
_EXCLUDED_DIRS = frozenset({"source"})

_ASSETS_ROOT = Path(__file__).resolve().parent
_IMAGES_DIR = _ASSETS_ROOT / "images"
_MANIFEST_PATH = _ASSETS_ROOT / "asset_manifest.json"


class AssetLoader:
    """Discover food image categories and load/cache card images."""

    def __init__(self) -> None:
        self._image_cache: dict[tuple[str, str], pygame.Surface] = {}
        self._scaled_cache: dict[tuple[str, str, tuple[int, int]], pygame.Surface] = {}

    # ------------------------------------------------------------------
    # Category and image discovery
    # ------------------------------------------------------------------

    def categories(self) -> list[str]:
        """Return sorted list of category subfolder names under images/."""
        return sorted(
            d.name
            for d in _IMAGES_DIR.iterdir()
            if d.is_dir() and d.name not in _EXCLUDED_DIRS
        )

    def image_ids(self, category: str) -> list[str]:
        """Return sorted list of image stem names in *category*."""
        cat_dir = _IMAGES_DIR / category
        if not cat_dir.is_dir():
            raise FileNotFoundError(f"Category directory not found: {cat_dir}")
        return sorted(p.stem for p in cat_dir.iterdir() if p.suffix.lower() == ".png")

    # ------------------------------------------------------------------
    # Image loading and scaling
    # ------------------------------------------------------------------

    def get_image(self, category: str, image_id: str) -> pygame.Surface:
        """Load and cache the master 333×333 image for *image_id*."""
        key = (category, image_id)
        if key not in self._image_cache:
            path = _IMAGES_DIR / category / f"{image_id}.png"
            if not path.is_file():
                raise FileNotFoundError(f"Image not found: {path}")
            self._image_cache[key] = pygame.image.load(str(path)).convert_alpha()
        return self._image_cache[key]

    def get_image_scaled(
        self, category: str, image_id: str, size: tuple[int, int]
    ) -> pygame.Surface:
        """Return *image_id* scaled to *size*, cached per (category, id, size)."""
        key = (category, image_id, size)
        if key not in self._scaled_cache:
            master = self.get_image(category, image_id)
            self._scaled_cache[key] = pygame.transform.smoothscale(master, size)
        return self._scaled_cache[key]

    # ------------------------------------------------------------------
    # Random pair sampling
    # ------------------------------------------------------------------

    def sample_pairs(self, category: str, n: int) -> list[str]:
        """Draw *n* distinct image IDs and return each twice (shuffled).

        Raises ``ValueError`` if *n* exceeds the number of images in
        the category.
        """
        ids = self.image_ids(category)
        if n > len(ids):
            raise ValueError(
                f"Requested {n} pairs but category '{category}' has only {len(ids)} images"
            )
        chosen = random.sample(ids, n)
        pairs = chosen * 2
        random.shuffle(pairs)
        return pairs

    # ------------------------------------------------------------------
    # Manifest validation
    # ------------------------------------------------------------------

    def validate_manifest(self) -> list[str]:
        """Check that every discovered image has a manifest entry.

        Returns a list of violation messages (empty = fully compliant).
        """
        violations: list[str] = []
        if not _MANIFEST_PATH.is_file():
            return [f"Manifest file not found: {_MANIFEST_PATH}"]

        with open(_MANIFEST_PATH, encoding="utf-8") as f:
            manifest: dict[str, dict[str, str]] = json.load(f)

        for category in self.categories():
            for image_id in self.image_ids(category):
                entry = manifest.get(image_id)
                if entry is None:
                    violations.append(f"Missing manifest entry: {image_id}")
                    continue
                if not entry.get("source_url"):
                    violations.append(f"Empty source_url: {image_id}")
                if not entry.get("licence"):
                    violations.append(f"Empty licence: {image_id}")
        return violations
