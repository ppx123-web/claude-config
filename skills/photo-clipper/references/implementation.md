# Photo Clipper Implementation Details

## Technical Overview

Photo Clipper uses GPT-5 vision API to analyze photos and generate intelligent cropping suggestions based on natural language prompts.

## API Integration

### OpenRouter GPT-5 Vision API

**Endpoint**: `https://openrouter.ai/api/v1/chat/completions`

**Authentication**:
```bash
export OPENROUTER_API_KEY="your-key-here"
```

### API Request Format

```python
import requests
import base64

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def analyze_photo(image_path, prompt):
    """Analyze photo using GPT-5 vision"""
    base64_image = encode_image(image_path)

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-5-vision",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        }
    )
    return response.json()
```

### Prompt Engineering

**Clipping Prompt Template**:
```
Analyze this photo and suggest intelligent cropping based on: {user_prompt}

Provide your response as JSON:
{
  "top_percentage": 0-100,
  "bottom_percentage": 0-100,
  "left_percentage": 0-100,
  "right_percentage": 0-100,
  "reasoning": "explanation of why this crop works",
  "confidence": 0.0-1.0
}

Constraints:
- Maximum 50% removal per dimension
- Preserve main subject
- Improve composition
```

## Image Processing

### Cropping Algorithm

```python
from PIL import Image

def crop_photo(image_path, top_pct, bottom_pct, left_pct, right_pct, output_path):
    """Crop photo based on percentage dimensions"""

    # Open image
    img = Image.open(image_path)
    width, height = img.size

    # Calculate pixel values
    top = int(height * top_pct / 100)
    bottom = int(height * (100 - bottom_pct) / 100)
    left = int(width * left_pct / 100)
    right = int(width * (100 - right_pct) / 100)

    # Validate crop dimensions
    total_removed = top_pct + bottom_pct
    if total_removed > 50:
        raise ValueError(f"Cannot remove {total_removed}% from height (max 50%)")

    # Crop image
    cropped = img.crop((left, top, right, bottom))

    # Save result
    cropped.save(output_path)
    return output_path
```

### File Naming

```python
def generate_output_path(input_path):
    """Generate output filename"""
    base, ext = os.path.splitext(input_path)
    return f"{base}-clipped{ext}"
```

## Error Handling

### API Errors

```python
def safe_clip(image_path, prompt):
    """Clip photo with fallback"""
    try:
        # Try GPT-5 analysis
        suggestion = analyze_photo(image_path, prompt)

        # Validate response
        if validate_crop_suggestion(suggestion):
            return apply_crop(image_path, suggestion)
        else:
            return fallback_crop(image_path)

    except requests.RequestException as e:
        logger.error(f"API error: {e}")
        return fallback_crop(image_path)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return fallback_crop(image_path)
```

### Validation Rules

```python
def validate_crop_suggestion(suggestion):
    """Validate crop suggestion from API"""
    required_fields = ['top_percentage', 'bottom_percentage',
                      'left_percentage', 'right_percentage']

    # Check all fields present
    if not all(field in suggestion for field in required_fields):
        return False

    # Check ranges (0-100)
    for field in required_fields:
        if not 0 <= suggestion[field] <= 100:
            return False

    # Check max removal per dimension (50%)
    total_vertical = suggestion['top_percentage'] + suggestion['bottom_percentage']
    total_horizontal = suggestion['left_percentage'] + suggestion['right_percentage']

    if total_vertical > 50 or total_horizontal > 50:
        logger.warning(f"Unsafe crop suggested: {suggestion}")
        return False

    return True
```

## Performance Optimization

### Image Resizing

```python
def resize_for_api(image_path, max_size=2048):
    """Resize image to reduce API cost and latency"""
    img = Image.open(image_path)

    # Calculate new dimensions (maintain aspect ratio)
    ratio = min(max_size / img.width, max_size / img.height)
    if ratio < 1:
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # Save to temp file
    temp_path = f"/tmp/resized_{os.path.basename(image_path)}"
    img.save(temp_path, quality=85)
    return temp_path
```

### Caching

```python
import hashlib

def get_cache_key(image_path, prompt):
    """Generate cache key for API response"""
    with open(image_path, "rb") as f:
        image_hash = hashlib.md5(f.read()).hexdigest()
    return hashlib.md5(f"{image_hash}:{prompt}".encode()).hexdigest()
```

## Configuration

### Environment Variables

```bash
# Required
OPENROUTER_API_KEY=sk-or-...

# Optional
MAX_CROP_PERCENTAGE=50      # Max removal per dimension
API_TIMEOUT=30              # API request timeout (seconds)
CACHE_ENABLED=true          # Enable response caching
MAX_IMAGE_SIZE=2048         # Max dimension for API (pixels)
```

### Settings

```python
DEFAULT_CONFIG = {
    'max_crop_percentage': 50,
    'api_timeout': 30,
    'cache_enabled': True,
    'max_image_size': 2048,
    'confidence_threshold': 0.7,
    'fallback_to_no_crop': True
}
```

## Testing

### Unit Tests

```python
def test_crop_validation():
    """Test crop suggestion validation"""
    # Valid crop
    assert validate_crop_suggestion({
        'top_percentage': 10,
        'bottom_percentage': 10,
        'left_percentage': 5,
        'right_percentage': 5
    }) == True

    # Exceeds max removal
    assert validate_crop_suggestion({
        'top_percentage': 30,
        'bottom_percentage': 30,
        'left_percentage': 0,
        'right_percentage': 0
    }) == False

    # Out of range
    assert validate_crop_suggestion({
        'top_percentage': 150,
        'bottom_percentage': 0,
        'left_percentage': 0,
        'right_percentage': 0
    }) == False
```

### Integration Tests

```python
def test_end_to_end_clip():
    """Test complete clipping workflow"""
    input_path = "test_photo.jpg"
    prompt = "Remove 20% from top"

    output_path = main(input_path, prompt)

    assert os.path.exists(output_path)
    assert "-clipped" in output_path
    assert file_size(output_path) < file_size(input_path)
```

## Dependencies

```python
# requirements.txt
Pillow>=10.0.0      # Image processing
requests>=2.31.0    # HTTP client
python-dotenv>=1.0.0 # Environment variables
```

## Best Practices

1. **Always validate user input**: Check file exists, format supported
2. **Never overwrite originals**: Always create new file
3. **Provide clear feedback**: Show what was removed and why
4. **Fail gracefully**: Fallback to safe defaults on errors
5. **Respect API limits**: Implement rate limiting and caching
6. **Log everything**: Help debugging with detailed logs
