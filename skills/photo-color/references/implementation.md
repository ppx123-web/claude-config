# Photo Color Implementation Details

## Technical Overview

Photo Color uses GPT-5 text API to interpret natural language prompts and calculate color adjustments (brightness, contrast, saturation) for photos.

## API Integration

### OpenRouter GPT-5 Text API

**Endpoint**: `https://openrouter.ai/api/v1/chat/completions`

**Authentication**:
```bash
export OPENROUTER_API_KEY="your-key-here"
```

### API Request Format

```python
import requests

def analyze_photo_prompt(user_prompt, current_brightness, current_contrast, current_saturation):
    """Get color adjustment suggestions from GPT-5"""

    system_prompt = """You are a photo enhancement expert. Given a user's prompt and current photo stats,
suggest color adjustments (brightness, contrast, saturation multipliers).

Respond ONLY with valid JSON:
{
  "suggestions": [
    {
      "style": "vivid" | "natural" | "dramatic" | "custom",
      "brightness_multiplier": 0.5-2.0,
      "contrast_multiplier": 0.5-2.0,
      "saturation_multiplier": 0.5-2.0,
      "reasoning": "explanation",
      "match_score": 0.0-1.0
    }
  ]
}

Constraints:
- All multipliers must be in range [0.5, 2.0]
- Higher multipliers = more intense effect
- Base multiplier is 1.0 (no change)
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-5",
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"""User prompt: "{user_prompt}"

Current photo stats:
- Brightness: {current_brightness}
- Contrast: {current_contrast}
- Saturation: {current_saturation}

Suggest 3 different enhancement approaches."""
                }
            ]
        }
    )
    return response.json()
```

## Photo Analysis

### Calculate Current Statistics

```python
from PIL import Image, ImageStat, ImageEnhance
import numpy as np

def analyze_photo(image_path):
    """Calculate current brightness, contrast, saturation"""

    img = Image.open(image_path).convert('RGB')

    # Convert to numpy array for calculations
    img_array = np.array(img)

    # Brightness: Mean pixel value (0-255)
    brightness = np.mean(img_array)

    # Contrast: Standard deviation of pixel values
    contrast = np.std(img_array)

    # Saturation: Mean of colorfulness metric
    # Convert to HSV
    hsv_img = img.convert('HSV')
    h, s, v = hsv_img.split()
    saturation = np.mean(np.array(s))

    # Normalize to 0-100 scale
    return {
        'brightness': (brightness / 255) * 100,
        'contrast': (contrast / 255) * 100,
        'saturation': (saturation / 255) * 100
    }
```

## Color Enhancement

### Apply Adjustments

```python
from PIL import ImageEnhance

def enhance_photo(image_path, brightness_mult, contrast_mult, saturation_mult, output_path):
    """Apply color enhancements to photo"""

    img = Image.open(image_path)

    # Apply brightness
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brightness_mult)

    # Apply contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast_mult)

    # Apply saturation (color)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation_mult)

    # Save result
    img.save(output_path, quality=95)
    return output_path
```

### Style Categories

**Vivid** (High saturation, increased brightness/contrast):
```python
{
    'brightness_multiplier': 1.1-1.3,
    'contrast_multiplier': 1.2-1.4,
    'saturation_multiplier': 1.4-1.6,
    'reasoning': 'Boost colors for vibrant, eye-catching look'
}
```

**Natural** (Subtle adjustments):
```python
{
    'brightness_multiplier': 1.05-1.15,
    'contrast_multiplier': 1.05-1.15,
    'saturation_multiplier': 1.1-1.25,
    'reasoning': 'Subtle enhancement while maintaining natural look'
}
```

**Dramatic** (High contrast, bold adjustments):
```python
{
    'brightness_multiplier': 0.9-1.1,
    'contrast_multiplier': 1.5-1.8,
    'saturation_multiplier': 1.2-1.5,
    'reasoning': 'Bold, cinematic look with strong contrast'
}
```

## Prompt Matching Algorithm

```python
def select_best_suggestion(suggestions, user_prompt):
    """Select best matching suggestion based on keywords"""

    prompt_lower = user_prompt.lower()

    # Keyword to style mapping
    style_keywords = {
        'vivid': ['vibrant', 'vivid', 'colorful', 'pop', 'bright colors',
                  'saturation', 'more color', 'intense'],
        'natural': ['natural', 'subtle', 'soft', 'gentle', 'light',
                    'realistic', 'authentic'],
        'dramatic': ['dramatic', 'bold', 'intense', 'cinematic', 'moody',
                     'high contrast', 'striking']
    }

    # Score each suggestion
    best_suggestion = None
    best_score = 0

    for suggestion in suggestions:
        style = suggestion['style']
        score = suggestion['match_score']

        # Boost score if keywords match
        if style in style_keywords:
            keyword_matches = sum(1 for kw in style_keywords[style]
                                 if kw in prompt_lower)
            score += keyword_matches * 0.1

        if score > best_score:
            best_score = score
            best_suggestion = suggestion

    return best_suggestion
```

## Error Handling

### Fallback Defaults

```python
def safe_enhance(image_path, user_prompt):
    """Enhance photo with fallback"""

    try:
        # Analyze current state
        stats = analyze_photo(image_path)

        # Get suggestions from GPT-5
        suggestions = analyze_photo_prompt(
            user_prompt,
            stats['brightness'],
            stats['contrast'],
            stats['saturation']
        )

        # Select best suggestion
        best = select_best_suggestion(suggestions, user_prompt)

        if best and validate_multipliers(best):
            return apply_enhancement(image_path, best)
        else:
            return fallback_enhancement(image_path)

    except Exception as e:
        logger.error(f"Enhancement error: {e}")
        return fallback_enhancement(image_path)
```

### Validation

```python
def validate_multipliers(suggestion):
    """Validate enhancement multipliers are in safe range"""

    multipliers = [
        suggestion['brightness_multiplier'],
        suggestion['contrast_multiplier'],
        suggestion['saturation_multiplier']
    ]

    for m in multipliers:
        if not 0.5 <= m <= 2.0:
            logger.warning(f"Multiplier {m} out of range [0.5, 2.0]")
            return False

    return True
```

### Fallback Enhancement

```python
def fallback_enhancement(image_path):
    """Safe default enhancement when API fails"""

    output_path = generate_output_path(image_path)

    # Conservative adjustments
    enhance_photo(
        image_path,
        brightness_mult=1.2,
        contrast_mult=1.1,
        saturation_mult=1.2,
        output_path=output_path
    )

    logger.info("Used fallback enhancement")
    return output_path
```

## Configuration

### Environment Variables

```bash
# Required
OPENROUTER_API_KEY=sk-or-...

# Optional
MIN_MULTIPLIER=0.5           # Minimum enhancement value
MAX_MULTIPLIER=2.0           # Maximum enhancement value
API_TIMEOUT=30               # API request timeout
DEFAULT_ENHANCEMENT=1.2      # Fallback saturation multiplier
```

### Settings

```python
DEFAULT_CONFIG = {
    'min_multiplier': 0.5,
    'max_multiplier': 2.0,
    'api_timeout': 30,
    'default_brightness': 1.2,
    'default_contrast': 1.1,
    'default_saturation': 1.2,
    'quality': 95  # JPEG quality
}
```

## Performance

### Optimization Tips

1. **Resize large images** before analysis (max 2048px)
2. **Cache analysis results** for repeated enhancements
3. **Batch processing** for multiple photos
4. **Parallel processing** with ThreadPoolExecutor

### Example Optimization

```python
from concurrent.futures import ThreadPoolExecutor

def batch_enhance(image_paths, prompts):
    """Enhance multiple photos in parallel"""

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(enhance_photo, path, prompt)
            for path, prompt in zip(image_paths, prompts)
        ]

        results = [f.result() for f in futures]

    return results
```

## Dependencies

```python
# requirements.txt
Pillow>=10.0.0      # Image processing
numpy>=1.24.0       # Numerical calculations
requests>=2.31.0    # HTTP client
python-dotenv>=1.0.0 # Environment variables
```

## Best Practices

1. **Analyze first**: Understand current photo state before enhancing
2. **Validate multipliers**: Always check ranges before applying
3. **Provide feedback**: Show user what adjustments were made
4. **Preserve quality**: Use high JPEG quality (95+)
5. **Fail gracefully**: Fallback to safe defaults on errors
6. **Non-destructive**: Never overwrite original photo
