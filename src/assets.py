# Implements: REQ-2 AC-2.1, AC-2.2, REQ-3 AC-3.1, AC-3.2, AC-3.3, AC-3.4 — Asset loading
# See: ARC §7 (assets)
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

import pygame


@dataclass
class CardImage:
    """A card face image with its identifier."""

    image_id: str
    surface: pygame.Surface


class AssetError(Exception):
    """Raised when an asset cannot be loaded."""


class AssetLoader:
    """Discovers image categories and loads card images from PNG files."""

    CARD_SIZE = (120, 120)

    def __init__(self, base_path: Path) -> None:
        self._base_path = base_path

    def list_categories(self) -> list[str]:
        """Return subfolder names under images/, excluding 'source'."""
        images_dir = self._base_path / "images"
        if not images_dir.is_dir():
            return []
        return sorted(
            d.name
            for d in images_dir.iterdir()
            if d.is_dir() and d.name != "source"
        )

    def load_card_images(self, category: str, count: int) -> list[CardImage]:
        """Load *count* random card face images from a category folder.

        Raises ``AssetError`` if the category folder is missing or has
        fewer images than requested.
        """
        category_dir = self._base_path / "images" / category
        if not category_dir.is_dir():
            raise AssetError(
                f"Category folder not found: {category_dir}"
            )

        png_files = sorted(category_dir.glob("*.png"))
        if len(png_files) < count:
            raise AssetError(
                f"Category '{category}' has {len(png_files)} images "
                f"but {count} are required"
            )

        selected = random.sample(png_files, count)
        images: list[CardImage] = []
        for path in selected:
            try:
                raw = pygame.image.load(str(path))
                if pygame.display.get_surface() is not None:
                    raw = raw.convert_alpha()
            except pygame.error as exc:
                raise AssetError(f"Failed to load image {path}: {exc}") from exc
            scaled = pygame.transform.smoothscale(raw, self.CARD_SIZE)
            images.append(CardImage(
                image_id=path.stem,
                surface=scaled,
            ))
        return images

    def load_card_back(self, color: tuple[int, int, int] = (0, 128, 60)) -> pygame.Surface:
        """Return a surface for the face-down card back."""
        w, h = self.CARD_SIZE
        surface = pygame.Surface(self.CARD_SIZE)
        surface.fill(color)
        # Draw a diamond pattern
        cx, cy = w // 2, h // 2
        points = [(cx, cy - 30), (cx + 20, cy), (cx, cy + 30), (cx - 20, cy)]
        pygame.draw.polygon(surface, (255, 255, 255), points, 2)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 8, 2)
        # Corner accents
        pygame.draw.circle(surface, (255, 255, 255), (12, 12), 4, 1)
        pygame.draw.circle(surface, (255, 255, 255), (w - 12, 12), 4, 1)
        pygame.draw.circle(surface, (255, 255, 255), (12, h - 12), 4, 1)
        pygame.draw.circle(surface, (255, 255, 255), (w - 12, h - 12), 4, 1)
        # Border
        pygame.draw.rect(surface, (255, 255, 255), (0, 0, w, h), 2, border_radius=6)
        return surface

    def validate_manifest(self) -> list[str]:
        """Check that every shipped image has an entry in the asset manifest.

        Returns a list of filename stems missing from the manifest.
        An empty list means the manifest is complete.
        """
        manifest_path = self._base_path / "asset_manifest.json"
        if not manifest_path.is_file():
            # No manifest — every image is "missing"
            all_stems = self._all_image_stems()
            return all_stems

        with open(manifest_path) as f:
            manifest = json.load(f)

        all_stems = self._all_image_stems()
        return [stem for stem in all_stems if stem not in manifest]

    def _all_image_stems(self) -> list[str]:
        """Return sorted filename stems for all PNGs under images/, excluding source/."""
        images_dir = self._base_path / "images"
        if not images_dir.is_dir():
            return []
        stems: list[str] = []
        for category_dir in sorted(images_dir.iterdir()):
            if not category_dir.is_dir() or category_dir.name == "source":
                continue
            for png in sorted(category_dir.glob("*.png")):
                stems.append(png.stem)
        return stems
