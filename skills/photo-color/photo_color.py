#!/usr/bin/env python
"""Photo Color Adjustment Script - Standalone

Adjust photo brightness, contrast, and saturation based on natural language prompts using GPT-5 text analysis.

Usage with uv:
    uv run python photo_color.py <photo_path> "<prompt>"

Requirements are automatically installed by uv from pyproject.toml.
"""

import json
import os
import re
from datetime import datetime
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

class ColorParams:
    """Configuration defining color enhancement adjustments."""

    def __init__(
        self,
        photo_path: Path,
        output_path: Path,
        saturation_multiplier: float,
        brightness_multiplier: float,
        contrast_multiplier: float,
        source: str,
        name: str | None = None,
        reasoning: str | None = None,
    ) -> None:
        self.photo_path: Final[Path] = photo_path
        self.output_path: Final[Path] = output_path
        self.saturation_multiplier: Final[float] = saturation_multiplier
        self.brightness_multiplier: Final[float] = brightness_multiplier
        self.contrast_multiplier: Final[float] = contrast_multiplier
        self.source: Final[str] = source
        self.name: Final[str | None] = name
        self.reasoning: Final[str | None] = reasoning
        self._validate()

    def _validate(self) -> None:
        # Validate multipliers (0.5-2.0)
        for name, value in [
            ("saturation_multiplier", self.saturation_multiplier),
            ("brightness_multiplier", self.brightness_multiplier),
            ("contrast_multiplier", self.contrast_multiplier),
        ]:
            if not isinstance(value, (int, float)):
                raise ValidationError(
                    f"{name} must be a number, got {type(value).__name__}",
                    f"Provide {name} as a float (0.5-2.0)",
                )
            if not (0.5 <= value <= 2.0):
                raise ValidationError(
                    f"{name} must be between 0.5 and 2.0, got {value}",
                    f"Adjust {name} to be within 0.5-2.0 range",
                )

        # Validate source
        valid_sources = {"gpt5-text", "manual"}
        base_source = self.source.split(":")[0] if ":" in self.source else self.source
        if base_source not in valid_sources:
            raise ValidationError(
                f"Invalid source: {self.source}",
                "Source must be 'gpt5-text' or 'manual'",
            )


class GPT5EnhancementSuggestion(BaseModel):
    """Single color enhancement suggestion from GPT-5 text API."""

    name: str = Field(min_length=1, max_length=100, description="Style name")
    saturation_multiplier: float = Field(ge=0.5, le=2.0, description="Saturation factor")
    brightness_multiplier: float = Field(ge=0.5, le=2.0, description="Brightness factor")
    contrast_multiplier: float = Field(ge=0.5, le=2.0, description="Contrast factor")
    reasoning: str = Field(min_length=1, max_length=500, description="Enhancement goals")
    style_category: str = Field(
        default="custom",
        pattern="^(vivid|natural|dramatic|custom)$",
        description="Style category"
    )

    def to_color_params(self, photo_path: Path, output_path: Path) -> ColorParams:
        """Convert GPT-5 suggestion to ColorParams model."""
        return ColorParams(
            photo_path=photo_path,
            output_path=output_path,
            saturation_multiplier=self.saturation_multiplier,
            brightness_multiplier=self.brightness_multiplier,
            contrast_multiplier=self.contrast_multiplier,
            source=f"gpt5-text:{self.style_category}",
            name=self.name,
            reasoning=self.reasoning,
        )


# =============================================================================
# GPT-5 Client
# =============================================================================

class GPT5Client:
    """GPT-5 client for text API calls."""

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

    def suggest_enhancements(
        self,
        brightness: float,
        contrast: float,
        saturation: float
    ) -> list[GPT5EnhancementSuggestion]:
        """Call GPT-5 text API to suggest color enhancement combinations."""
        try:
            # Prepare prompt
            prompt = f"""Based on photo analysis (brightness: {brightness:.2f}, contrast: {contrast:.2f}, saturation: {saturation:.2f}), suggest 3-5 color enhancement combinations.

IMPORTANT: You must respond with valid JSON only. No markdown, no code blocks, no explanations outside the JSON.

For each suggestion, provide:
- name: descriptive style name (e.g., "Vivid & Bright", "Natural & Soft")
- saturation_multiplier: saturation factor (0.5-2.0)
- brightness_multiplier: brightness factor (0.5-2.0)
- contrast_multiplier: contrast factor (0.5-2.0)
- reasoning: explanation of what this enhancement achieves
- style_category: one of "vivid", "natural", "dramatic", "custom"

Return JSON in this exact format:
{{
  "suggestions": [
    {{
      "name": "Style Name",
      "saturation_multiplier": 1.3,
      "brightness_multiplier": 1.1,
      "contrast_multiplier": 1.2,
      "reasoning": "Explanation here",
      "style_category": "vivid"
    }}
  ]
}}"""

            # Call API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=800,
            )

            content = response.choices[0].message.content
            if content is None:
                raise APIError("API returned empty response", "Check model availability")

            # Parse JSON
            parsed = self._parse_json(content)

            if parsed is None:
                # Fallback defaults
                return [
                    GPT5EnhancementSuggestion(
                        name="Balanced Enhancement",
                        saturation_multiplier=1.2,
                        brightness_multiplier=1.1,
                        contrast_multiplier=1.1,
                        reasoning="API returned invalid JSON - using safe defaults",
                        style_category="natural",
                    ),
                    GPT5EnhancementSuggestion(
                        name="Vivid & Bright",
                        saturation_multiplier=1.3,
                        brightness_multiplier=1.1,
                        contrast_multiplier=1.2,
                        reasoning="Fallback option - increases saturation and brightness",
                        style_category="vivid",
                    ),
                    GPT5EnhancementSuggestion(
                        name="Muted & Soft",
                        saturation_multiplier=1.05,
                        brightness_multiplier=1.05,
                        contrast_multiplier=1.05,
                        reasoning="Fallback option - subtle enhancements",
                        style_category="natural",
                    ),
                ]

            # Extract suggestions
            suggestions_data = parsed.get("suggestions", [])

            if not suggestions_data:
                # Fallback defaults
                return [
                    GPT5EnhancementSuggestion(
                        name="Balanced Enhancement",
                        saturation_multiplier=1.2,
                        brightness_multiplier=1.1,
                        contrast_multiplier=1.1,
                        reasoning="API response missing suggestions - using safe defaults",
                        style_category="natural",
                    ),
                    GPT5EnhancementSuggestion(
                        name="Vivid & Bright",
                        saturation_multiplier=1.3,
                        brightness_multiplier=1.1,
                        contrast_multiplier=1.2,
                        reasoning="Fallback option - increases saturation and brightness",
                        style_category="vivid",
                    ),
                    GPT5EnhancementSuggestion(
                        name="Muted & Soft",
                        saturation_multiplier=1.05,
                        brightness_multiplier=1.05,
                        contrast_multiplier=1.05,
                        reasoning="Fallback option - subtle enhancements",
                        style_category="natural",
                    ),
                ]

            # Parse suggestions
            try:
                suggestions = [GPT5EnhancementSuggestion(**s) for s in suggestions_data[:5]]
            except (ValueError, TypeError) as e:
                # Fallback defaults
                return [
                    GPT5EnhancementSuggestion(
                        name="Balanced Enhancement",
                        saturation_multiplier=1.2,
                        brightness_multiplier=1.1,
                        contrast_multiplier=1.1,
                        reasoning=f"API returned invalid format ({str(e)[:50]}) - using safe defaults",
                        style_category="natural",
                    ),
                    GPT5EnhancementSuggestion(
                        name="Vivid & Bright",
                        saturation_multiplier=1.3,
                        brightness_multiplier=1.1,
                        contrast_multiplier=1.2,
                        reasoning="Fallback option - increases saturation and brightness",
                        style_category="vivid",
                    ),
                    GPT5EnhancementSuggestion(
                        name="Muted & Soft",
                        saturation_multiplier=1.05,
                        brightness_multiplier=1.05,
                        contrast_multiplier=1.05,
                        reasoning="Fallback option - subtle enhancements",
                        style_category="natural",
                    ),
                ]

            # Ensure we have 3-5 suggestions
            if len(suggestions) < 3:
                while len(suggestions) < 3:
                    suggestions.append(GPT5EnhancementSuggestion(
                        name=f"Option {len(suggestions) + 1}",
                        saturation_multiplier=1.0 + (len(suggestions) * 0.1),
                        brightness_multiplier=1.0 + (len(suggestions) * 0.05),
                        contrast_multiplier=1.0 + (len(suggestions) * 0.05),
                        reasoning="Additional suggestion to meet minimum requirements",
                        style_category="custom",
                    ))

            return suggestions[:5]

        except Exception as e:
            # Fallback to safe defaults
            return [
                GPT5EnhancementSuggestion(
                    name="Balanced Enhancement",
                    saturation_multiplier=1.2,
                    brightness_multiplier=1.1,
                    contrast_multiplier=1.1,
                    reasoning=f"API unavailable ({str(e)[:50]}) - using safe defaults",
                    style_category="natural",
                ),
                GPT5EnhancementSuggestion(
                    name="Vivid & Bright",
                    saturation_multiplier=1.3,
                    brightness_multiplier=1.1,
                    contrast_multiplier=1.2,
                    reasoning="Fallback option - increases saturation and brightness",
                    style_category="vivid",
                ),
                GPT5EnhancementSuggestion(
                    name="Muted & Soft",
                    saturation_multiplier=1.05,
                    brightness_multiplier=1.05,
                    contrast_multiplier=1.05,
                    reasoning="Fallback option - subtle enhancements",
                    style_category="natural",
                ),
            ]


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


def image_to_array(img: Image.Image) -> np.ndarray:
    """Convert PIL Image to numpy array."""
    return np.array(img)


def array_to_image(array: np.ndarray, mode: str = "RGB") -> Image.Image:
    """Convert numpy array to PIL Image."""
    array = np.clip(array, 0, 255).astype(np.uint8)
    return Image.fromarray(array, mode=mode)


# =============================================================================
# Enhancement Functions
# =============================================================================

def _select_best_suggestion(suggestions: list[GPT5EnhancementSuggestion], prompt: str) -> GPT5EnhancementSuggestion:
    """Select the best enhancement suggestion based on prompt keywords."""
    prompt_lower = prompt.lower()

    vivid_keywords = ["vibrant", "vivid", "colorful", "saturation", "bright", "pop"]
    natural_keywords = ["natural", "subtle", "soft", "gentle", "mild"]
    dramatic_keywords = ["dramatic", "bold", "intense", "strong", "contrast"]

    if any(kw in prompt_lower for kw in vivid_keywords):
        for suggestion in suggestions:
            if suggestion.style_category == "vivid":
                return suggestion
    elif any(kw in prompt_lower for kw in natural_keywords):
        for suggestion in suggestions:
            if suggestion.style_category == "natural":
                return suggestion
    elif any(kw in prompt_lower for kw in dramatic_keywords):
        for suggestion in suggestions:
            if suggestion.style_category == "dramatic":
                return suggestion

    return suggestions[0]


def _apply_enhancements(arr: np.ndarray, params: ColorParams) -> np.ndarray:
    """Apply all color enhancements in a single efficient pass."""
    result = arr.astype(float)

    # Apply brightness first
    result = result * params.brightness_multiplier

    # Apply contrast
    if len(arr.shape) == 3:
        mean = np.mean(result, axis=(0, 1), keepdims=True)
    else:
        mean = np.mean(result)

    result = mean + (result - mean) * params.contrast_multiplier

    # Apply saturation (in HSV)
    if len(arr.shape) == 3:
        img = Image.fromarray(arr.astype(np.uint8))
        hsv = img.convert("HSV")
        hsv_arr = np.array(hsv).astype(float)

        # Adjust saturation channel (index 1)
        hsv_arr[..., 1] = np.clip(hsv_arr[..., 1] * params.saturation_multiplier, 0, 255)

        # Convert back to RGB
        enhanced_hsv = Image.fromarray(hsv_arr.astype(np.uint8), mode="HSV")
        result = np.array(enhanced_hsv.convert("RGB")).astype(float)

    # Clip to valid range
    result = np.clip(result, 0, 255).astype(np.uint8)

    return result


def enhance_photo(photo_path: Path, prompt: str, output_path: Path | None = None) -> Path:
    """Enhance a photo based on natural language prompt.

    Args:
        photo_path: Path to input photo (JPG/PNG)
        prompt: Natural language description of desired adjustments
        output_path: Optional output path. If None, generates {photo_path.stem}-enhanced.{ext}

    Returns:
        Path to enhanced photo
    """
    # Validate inputs
    if not photo_path.exists():
        raise ValidationError(
            f"Photo file not found: {photo_path}",
            "Check the file path and ensure the file exists",
        )

    # Generate output path if not provided
    if output_path is None:
        output_path = photo_path.parent / f"{photo_path.stem}-enhanced{photo_path.suffix}"

    # Analyze photo
    print(f"\n📸 Analyzing photo: {photo_path.name}")
    print(f"📝 Prompt: {prompt}")

    img = load_image(photo_path)
    arr = image_to_array(img)

    # Calculate metrics
    brightness = float(np.mean(arr) / 255.0)
    contrast = float(np.std(arr) / 128.0)
    hsv = img.convert("HSV")
    hsv_arr = np.array(hsv)
    saturation = float(np.mean(hsv_arr[..., 1]) / 255.0)

    print(f"   Current state: brightness={brightness:.2f}, contrast={contrast:.2f}, saturation={saturation:.2f}")

    # Call GPT-5 text API
    try:
        client = GPT5Client()
        options = client.suggest_enhancements(brightness, contrast, saturation)

        # Select best suggestion
        suggestion = _select_best_suggestion(options, prompt)

        # Convert to ColorParams
        params = suggestion.to_color_params(photo_path, output_path)

        # Display GPT-5 recommendation
        print(f"\n✨ GPT-5 Enhancement Recommendation:")
        print(f"   Style: {suggestion.name}")
        print(f"   Saturation: ×{suggestion.saturation_multiplier:.2f}")
        print(f"   Brightness: ×{suggestion.brightness_multiplier:.2f}")
        print(f"   Contrast: ×{suggestion.contrast_multiplier:.2f}")
        print(f"   Reasoning: {suggestion.reasoning}")

    except Exception as e:
        print(f"⚠️  GPT-5 suggestion failed: {e}")
        print("ℹ️  Using safe defaults (balanced enhancement)")

        params = ColorParams(
            photo_path=photo_path,
            output_path=output_path,
            saturation_multiplier=1.2,
            brightness_multiplier=1.1,
            contrast_multiplier=1.1,
            source="manual",
            name="Balanced Enhancement",
            reasoning="GPT-5 unavailable - using safe defaults",
        )

    # Perform enhancement
    print(f"\n🎨 Enhancing photo...")

    img = load_image(photo_path)
    arr = image_to_array(img)

    # Apply enhancements
    enhanced_arr = _apply_enhancements(arr, params)

    # Convert back to image
    enhanced_img = array_to_image(enhanced_arr, mode=img.mode)

    # Save
    save_image(enhanced_img, params.output_path, format=img.format)

    # Report results
    print(f"✅ Enhanced photo saved to: {params.output_path}")
    print(f"   Saturation: ×{params.saturation_multiplier:.2f}")
    print(f"   Brightness: ×{params.brightness_multiplier:.2f}")
    print(f"   Contrast: ×{params.contrast_multiplier:.2f}")

    if params.name:
        print(f"   Style: {params.name}")

    if params.reasoning:
        print(f"   Reasoning: {params.reasoning}")

    return params.output_path


# =============================================================================
# Main Entry Point
# =============================================================================

def main(photo_path: str | Path, prompt: str, output_path: str | Path | None = None) -> str:
    """Main entry point for photo color enhancement.

    Args:
        photo_path: Path to input photo (string or Path object)
        prompt: Natural language description of desired adjustments
        output_path: Optional output path (string or Path object)

    Returns:
        Path to enhanced photo as string
    """
    photo_path = Path(photo_path) if isinstance(photo_path, str) else photo_path
    output_path = Path(output_path) if output_path and isinstance(output_path, str) else output_path

    result = enhance_photo(photo_path, prompt, output_path)
    return str(result)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python photo_color.py <photo_path> <prompt> [output_path]")
        print("\nExample:")
        print('  python photo_color.py photo.jpg "make the colors more vibrant and warm"')
        sys.exit(1)

    photo = Path(sys.argv[1])
    prompt_text = sys.argv[2]
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    result_path = main(photo, prompt_text, out)
    print(f"\n🎉 Success! Enhanced photo: {result_path}")
