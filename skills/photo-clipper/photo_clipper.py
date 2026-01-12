#!/usr/bin/env python
"""Photo Clipping Script - Standalone

Crop photos intelligently based on natural language prompts using GPT-5 vision analysis.

Usage with uv:
    uv run python photo_clipper.py <photo_path> "<prompt>"

Requirements are automatically installed by uv from pyproject.toml.
"""

import base64
import io
import json
import os
import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Final

import numpy as np
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field


# =============================================================================
# Configuration
# =============================================================================

load_dotenv()

API_URL = "https://openrouter.ai/api/v1"
MODEL = "openai/gpt-5.2"


# =============================================================================
# Exceptions
# =============================================================================

class APIError(Exception):
    """Raised when API request fails."""
    def __init__(self, message: str, recovery_hint: str | None = None) -> None:
        self.message = message
        self.recovery_hint = recovery_hint
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.recovery_hint:
            return f"{self.message}\n  Recovery: {self.recovery_hint}"
        return self.message


class ImageLoadError(Exception):
    """Raised when image loading fails."""
    def __init__(self, message: str, recovery_hint: str | None = None) -> None:
        self.message = message
        self.recovery_hint = recovery_hint
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.recovery_hint:
            return f"{self.message}\n  Recovery: {self.recovery_hint}"
        return self.message


class ValidationError(Exception):
    """Raised when input validation fails."""
    def __init__(self, message: str, recovery_hint: str | None = None) -> None:
        self.message = message
        self.recovery_hint = recovery_hint
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.recovery_hint:
            return f"{self.message}\n  Recovery: {self.recovery_hint}"
        return self.message


# =============================================================================
# Data Models
# =============================================================================

class ClippingParams:
    """Configuration defining rectangular region to extract from photo."""

    def __init__(
        self,
        photo_path: Path,
        output_path: Path,
        left_pct: float,
        right_pct: float,
        top_pct: float,
        bottom_pct: float,
        source: str,
        reasoning: str | None = None,
    ) -> None:
        self.photo_path: Final[Path] = photo_path
        self.output_path: Final[Path] = output_path
        self.left_pct: Final[float] = left_pct
        self.right_pct: Final[float] = right_pct
        self.top_pct: Final[float] = top_pct
        self.bottom_pct: Final[float] = bottom_pct
        self.source: Final[str] = source
        self.reasoning: Final[str | None] = reasoning
        self._validate()

    def _validate(self) -> None:
        # Validate percentages (0-100)
        for name, value in [
            ("left_pct", self.left_pct),
            ("right_pct", self.right_pct),
            ("top_pct", self.top_pct),
            ("bottom_pct", self.bottom_pct),
        ]:
            if not isinstance(value, (int, float)):
                raise ValidationError(
                    f"{name} must be a number, got {type(value).__name__}",
                    f"Provide {name} as a float (0.0-100.0)",
                )
            if not (0.0 <= value <= 100.0):
                raise ValidationError(
                    f"{name} must be between 0 and 100, got {value}",
                    f"Adjust {name} to be within 0-100 range",
                )

        # Validate source
        valid_sources = {"gpt5-vision", "manual"}
        base_source = self.source.split(":")[0] if ":" in self.source else self.source
        if base_source not in valid_sources:
            raise ValidationError(
                f"Invalid source: {self.source}", "Source must be 'gpt5-vision' or 'manual'"
            )

    def to_pixels(self, photo_width: int, photo_height: int) -> tuple[int, int, int, int]:
        """Convert percentages to pixel coordinates."""
        left_px = int(self.left_pct / 100.0 * photo_width)
        right_px = int(self.right_pct / 100.0 * photo_width)
        top_px = int(self.top_pct / 100.0 * photo_height)
        bottom_px = int(self.bottom_pct / 100.0 * photo_height)

        left = left_px
        right = photo_width - right_px
        top = top_px
        bottom = photo_height - bottom_px

        return left, right, top, bottom


class GPT5ClippingSuggestion(BaseModel):
    """GPT-5 vision API response for photo clipping suggestions."""

    left_pct: float = Field(ge=0.0, le=50.0, description="Percentage to remove from left edge")
    right_pct: float = Field(ge=0.0, le=50.0, description="Percentage to remove from right edge")
    top_pct: float = Field(ge=0.0, le=50.0, description="Percentage to remove from top edge")
    bottom_pct: float = Field(ge=0.0, le=50.0, description="Percentage to remove from bottom edge")
    reasoning: str = Field(min_length=1, max_length=1000, description="Human-readable explanation")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in recommendation", default=0.8)

    def to_clipping_params(self, photo_path: Path, output_path: Path) -> ClippingParams:
        """Convert GPT-5 suggestion to ClippingParams model."""
        return ClippingParams(
            photo_path=photo_path,
            output_path=output_path,
            left_pct=self.left_pct,
            right_pct=self.right_pct,
            top_pct=self.top_pct,
            bottom_pct=self.bottom_pct,
            source=f"gpt5-vision:{self.confidence_score:.2f}",
            reasoning=self.reasoning,
        )

    def validate_minimum_size(self, photo_width: int, photo_height: int) -> bool:
        """Check if clipping preserves at least 50% of original dimensions."""
        width_remaining_pct = 100 - self.left_pct - self.right_pct
        height_remaining_pct = 100 - self.top_pct - self.bottom_pct
        return width_remaining_pct >= 50 and height_remaining_pct >= 50


# =============================================================================
# GPT-5 Client
# =============================================================================

class GPT5Client:
    """GPT-5 client for vision API calls."""

    def __init__(self, api_key: str | None = None) -> None:
        if api_key is None:
            api_key = os.environ.get("OPENROUTER_API_KEY")

        if not api_key:
            raise APIError(
                "OpenRouter API key not found",
                "Set OPENROUTER_API_KEY environment variable",
            )

        self.client = OpenAI(base_url=API_URL, api_key=api_key)
        self.model = MODEL

    def _encode_image(self, photo_path: Path, max_size: int = 2048) -> str:
        """Load photo, resize if needed, and encode to base64 data URI."""
        with Image.open(photo_path) as img:
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.read()).decode('utf-8')

            return f"data:image/jpeg;base64,{img_base64}"

    def _parse_json(self, content: str, max_attempts: int = 2) -> dict | None:
        """Parse JSON from API response with retry."""
        for attempt in range(max_attempts):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try markdown code blocks
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        pass

                json_match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        pass

                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        pass

                if attempt == max_attempts - 1:
                    return None

        return None

    def suggest_clipping(self, photo_path: Path) -> GPT5ClippingSuggestion:
        """Call GPT-5 vision API to suggest clipping percentages."""
        try:
            # Encode image
            image_data = self._encode_image(photo_path)

            # Prepare prompt
            prompt = """Analyze this photo and suggest clipping percentages for optimal composition.

Apply these professional photography composition rules:
1. Rule of Thirds: Align main subjects or horizons with the grid lines.
2. Remove Distractions: Crop out partial objects, bright spots, or clutter on edges.
3. Balance & Symmetry: If the image is symmetrical, maintain it. If not, balance the visual weight.
4. Lead Room: Give moving subjects space to "move into".
5. Fill the Frame: If the background is irrelevant, crop tighter to emphasize the subject.

IMPORTANT: You must respond with valid JSON only. No markdown, no code blocks, no explanations outside the JSON.

Return JSON in this exact format:
{
  "right": 5.0,
  "left": 5.0,
  "top": 10.0,
  "bottom": 5.0,
  "reasoning": "Brief explanation of the composition choices"
}

Where:
- right: percentage to remove from LEFT edge (0-50%)
- left: percentage to remove from RIGHT edge (0-50%)
- top: percentage to remove from TOP edge (0-50%)
- bottom: percentage to remove from BOTTOM edge (0-50%)
- reasoning: explanation of what elements were removed and why (max 1000 characters)

Keep total removal under 50% per dimension to preserve image quality."""

            # Call API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data}}
                    ]
                }],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=500,
            )

            content = response.choices[0].message.content
            if content is None:
                raise APIError("API returned empty response", "Check model availability")

            # Parse JSON
            parsed = self._parse_json(content)

            if parsed is None:
                return GPT5ClippingSuggestion(
                    left_pct=0.0, right_pct=0.0, top_pct=0.0, bottom_pct=0.0,
                    reasoning="API returned invalid JSON - using safe defaults",
                    confidence_score=0.0,
                )

            # Validate fields
            required_fields = ["right", "left", "top", "bottom", "reasoning"]
            if any(f not in parsed for f in required_fields):
                return GPT5ClippingSuggestion(
                    left_pct=0.0, right_pct=0.0, top_pct=0.0, bottom_pct=0.0,
                    reasoning="API response missing fields - using safe defaults",
                    confidence_score=0.0,
                )

            return GPT5ClippingSuggestion(
                left_pct=float(parsed.get("right", 0.0)),
                right_pct=float(parsed.get("left", 0.0)),
                top_pct=float(parsed.get("top", 0.0)),
                bottom_pct=float(parsed.get("bottom", 0.0)),
                reasoning=parsed.get("reasoning", "No reasoning")[:1000],
                confidence_score=float(parsed.get("confidence", 0.8)),
            )

        except Exception as e:
            # Fallback to safe defaults
            return GPT5ClippingSuggestion(
                left_pct=0.0, right_pct=0.0, top_pct=0.0, bottom_pct=0.0,
                reasoning=f"API unavailable ({str(e)[:100]}) - using safe defaults",
                confidence_score=0.0,
            )


# =============================================================================
# Image I/O Utilities
# =============================================================================

def load_image(path: Path) -> Image.Image:
    """Load an image file with validation."""
    if not path.exists():
        raise ImageLoadError(
            f"Image file not found: {path}",
            "Check the file path and ensure the file exists",
        )

    if not path.is_file():
        raise ImageLoadError(
            f"Path is not a file: {path}",
            "Provide a path to an image file, not a directory",
        )

    valid_extensions = {".jpg", ".jpeg", ".png"}
    if path.suffix.lower() not in valid_extensions:
        raise ImageLoadError(
            f"Unsupported image format: {path.suffix}",
            "Use JPEG (.jpg, .jpeg) or PNG (.png) files",
        )

    try:
        img = Image.open(path)
        img.verify()
        img = Image.open(path)  # Reopen after verify
        return img
    except Exception as e:
        raise ImageLoadError(
            f"Failed to load image: {e}",
            "Ensure the file is a valid JPEG or PNG image",
        ) from e


def save_image(img: Image.Image, output_path: Path, format: str | None = None, quality: int = 95) -> None:
    """Save an image file with validation."""
    if not output_path.parent.exists():
        raise ImageLoadError(
            f"Output directory does not exist: {output_path.parent}",
            f"Create the directory first: mkdir -p {output_path.parent}",
        )

    if not output_path.parent.is_dir():
        raise ImageLoadError(
            f"Output path is not a directory: {output_path.parent}",
            "Provide a valid directory path for the output",
        )

    if format is None:
        ext = output_path.suffix.lower()
        if ext in {".jpg", ".jpeg"}:
            format = "JPEG"
        elif ext == ".png":
            format = "PNG"
        else:
            raise ImageLoadError(
                f"Cannot infer format from extension: {ext}",
                "Use .jpg, .jpeg, or .png extension",
            )

    try:
        if format == "JPEG" and img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background

        save_kwargs = {}
        if format == "JPEG":
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        elif format == "PNG":
            save_kwargs["optimize"] = True

        img.save(output_path, format=format, **save_kwargs)
    except Exception as e:
        raise ImageLoadError(
            f"Failed to save image: {e}",
            "Check disk space and write permissions",
        ) from e


# =============================================================================
# Main Clipping Function
# =============================================================================

def clip_photo(photo_path: Path, prompt: str, output_path: Path | None = None) -> Path:
    """Clip a photo based on natural language prompt.

    Args:
        photo_path: Path to input photo (JPG/PNG)
        prompt: Natural language description of desired cropping
        output_path: Optional output path. If None, generates {photo_path.stem}-clipped.{ext}

    Returns:
        Path to clipped photo
    """
    # Validate inputs
    if not photo_path.exists():
        raise ValidationError(
            f"Photo file not found: {photo_path}",
            "Check the file path and ensure the file exists",
        )

    # Generate output path if not provided
    if output_path is None:
        output_path = photo_path.parent / f"{photo_path.stem}-clipped{photo_path.suffix}"

    # Call GPT-5 vision API
    print(f"\n📸 Analyzing photo: {photo_path.name}")
    print(f"📝 Prompt: {prompt}")

    try:
        client = GPT5Client()
        suggestion = client.suggest_clipping(photo_path)

        # Validate minimum size
        img = Image.open(photo_path)
        if not suggestion.validate_minimum_size(img.width, img.height):
            print("⚠️  Warning: GPT-5 suggestion would crop too much, using safe defaults")
            suggestion = GPT5ClippingSuggestion(
                left_pct=0.0, right_pct=0.0, top_pct=0.0, bottom_pct=0.0,
                reasoning="GPT-5 suggestion too aggressive - using safe defaults",
                confidence_score=0.0,
            )

        # Convert to ClippingParams
        params = suggestion.to_clipping_params(photo_path, output_path)

        # Display GPT-5 reasoning
        print(f"\n✨ GPT-5 Clipping Suggestion:")
        print(f"   Remove: {suggestion.left_pct}% left, {suggestion.right_pct}% right, "
              f"{suggestion.top_pct}% top, {suggestion.bottom_pct}% bottom")
        print(f"   Confidence: {suggestion.confidence_score:.0%}")
        print(f"   Reasoning: {suggestion.reasoning}")

    except Exception as e:
        print(f"⚠️  GPT-5 suggestion failed: {e}")
        print("ℹ️  Using safe defaults (no clipping)")

        params = ClippingParams(
            photo_path=photo_path,
            output_path=output_path,
            left_pct=0.0, right_pct=0.0, top_pct=0.0, bottom_pct=0.0,
            source="manual",
            reasoning="GPT-5 unavailable - using safe defaults",
        )

    # Perform clipping
    print(f"\n✂️  Clipping photo...")

    img = load_image(photo_path)
    width, height = img.size

    # Convert percentages to pixels
    left, right, top, bottom = params.to_pixels(width, height)

    # Validate region
    if left >= right or top >= bottom:
        raise ValidationError(
            f"Invalid clipping region: left={left}, right={right}, top={top}, bottom={bottom}",
            "Ensure left < right and top < bottom",
        )

    # Check bounds
    if left >= width or right <= 0 or top >= height or bottom <= 0:
        print("⚠️  Warning: Clipping region outside photo bounds")
        left = max(0, min(left, width - 1))
        right = max(1, min(right, width))
        top = max(0, min(top, height - 1))
        bottom = max(1, min(bottom, height))
        print(f"   Adjusted to: left={left}px, right={right}px, top={top}px, bottom={bottom}px")

    # Crop
    crop_box = (left, top, right, bottom)
    try:
        cropped = img.crop(crop_box)
        save_image(cropped, params.output_path, format=img.format)

        print(f"✅ Clipped photo saved to: {params.output_path}")
        print(f"   Original: {width}x{height}")
        print(f"   Clipped: {cropped.size[0]}x{cropped.size[1]}")
        print(f"   Removed: {params.left_pct}% left, {params.right_pct}% right, "
              f"{params.top_pct}% top, {params.bottom_pct}% bottom")

        if params.reasoning:
            print(f"   Reasoning: {params.reasoning}")

        return params.output_path

    except Exception as e:
        raise ValidationError(
            f"Failed to clip photo: {e}",
            "Check clipping parameters and photo format",
        ) from e


# =============================================================================
# Main Entry Point
# =============================================================================

def main(photo_path: str | Path, prompt: str, output_path: str | Path | None = None) -> str:
    """Main entry point for photo clipping.

    Args:
        photo_path: Path to input photo (string or Path object)
        prompt: Natural language description of desired cropping
        output_path: Optional output path (string or Path object)

    Returns:
        Path to clipped photo as string
    """
    photo_path = Path(photo_path) if isinstance(photo_path, str) else photo_path
    output_path = Path(output_path) if output_path and isinstance(output_path, str) else output_path

    result = clip_photo(photo_path, prompt, output_path)
    return str(result)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python photo_clipper.py <photo_path> <prompt> [output_path]")
        print("\nExample:")
        print('  python photo_clipper.py photo.jpg "crop to focus on the mountain in the center"')
        sys.exit(1)

    photo = Path(sys.argv[1])
    prompt_text = sys.argv[2]
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    result_path = main(photo, prompt_text, out)
    print(f"\n🎉 Success! Clipped photo: {result_path}")
