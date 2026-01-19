# Photo Color Examples

## Example 1: Vivid Colors

### User Request

```
让这张照片的颜色更鲜艳、更生动
```

### AI Action

```python
from photo_color import main

result = main(
    photo_path="sunset.jpg",
    prompt="Make the colors much more vibrant and vivid"
)
```

### Output

✅ **Enhanced photo saved**: `sunset-enhanced.jpg`

**Photo Analysis**:
- Original brightness: 65/100
- Original contrast: 55/100
- Original saturation: 48/100

**GPT-5 Selected Style**: Vivid

**Applied Adjustments**:
- Brightness: ×1.15 (65 → 75)
- Contrast: ×1.35 (55 → 74)
- Saturation: ×1.50 (48 → 72)

**Reasoning**: "User wants vibrant colors. High saturation multiplier (1.5) with increased contrast creates eye-catching, vivid appearance."

---

## Example 2: Natural Enhancement

### User Request

```
稍微增强一下，但保持自然
```

### AI Action

```python
result = main(
    photo_path="portrait.jpg",
    prompt="Apply a subtle natural enhancement"
)
```

### Output

✅ **Enhanced photo saved**: `portrait-enhanced.jpg`

**Photo Analysis**:
- Original brightness: 58/100
- Original contrast: 52/100
- Original saturation: 45/100

**GPT-5 Selected Style**: Natural

**Applied Adjustments**:
- Brightness: ×1.08 (58 → 63)
- Contrast: ×1.10 (52 → 57)
- Saturation: ×1.18 (45 → 53)

**Reasoning**: "Subtle adjustments (1.05-1.2 range) enhance photo while maintaining realistic, natural appearance."

---

## Example 3: Dramatic Cinematic Look

### User Request

```
创建一个戏剧性的电影效果，高对比度
```

### AI Action

```python
result = main(
    photo_path="cityscape.jpg",
    prompt="Create a dramatic cinematic look with high contrast"
)
```

### Output

✅ **Enhanced photo saved**: `cityscape-enhanced.jpg`

**Photo Analysis**:
- Original brightness: 62/100
- Original contrast: 50/100
- Original saturation: 55/100

**GPT-5 Selected Style**: Dramatic

**Applied Adjustments**:
- Brightness: ×0.95 (62 → 59) - slightly darker
- Contrast: ×1.65 (50 → 82) - much higher contrast
- Saturation: ×1.35 (55 → 74)

**Reasoning**: "Dramatic look achieved through high contrast (1.65) and slightly reduced brightness. Creates moody, cinematic atmosphere."

---

## Example 4: Fix Washed Out Colors

### User Request

```
修复这张照片褪色的外观，增加饱和度
```

### AI Action

```python
result = main(
    photo_path="old-photo.jpg",
    prompt="Fix the washed out appearance, increase saturation to make colors more realistic"
)
```

### Output

✅ **Enhanced photo saved**: `old-photo-enhanced.jpg`

**Photo Analysis**:
- Original brightness: 78/100 - too bright
- Original contrast: 42/100 - low contrast
- Original saturation: 35/100 - washed out

**GPT-5 Selected Style**: Vivid

**Applied Adjustments**:
- Brightness: ×0.92 (78 → 72) - reduce brightness
- Contrast: ×1.30 (42 → 55) - increase contrast
- Saturation: ×1.45 (35 → 51) - major saturation boost

**Reasoning**: "Photo is washed out with low saturation (35) and high brightness (78). Reducing brightness while boosting saturation and contrast restores color vibrancy."

---

## Example 5: Add Warmth

### User Request

```
给照片增加暖色调
```

### AI Action

```python
result = main(
    photo_path="winter.jpg",
    prompt="Add warmth to the photo"
)
```

### Output

✅ **Enhanced photo saved**: `winter-enhanced.jpg`

**GPT-5 Selected Style**: Custom (Warm)

**Applied Adjustments**:
- Brightness: ×1.12
- Contrast: ×1.15
- Saturation: ×1.25

**Reasoning**: "Warmth achieved through slight brightness increase (1.12) combined with boosted saturation (1.25) for golden, warm tone."

---

## Example 6: Brighten and Increase Contrast

### User Request

```
提亮照片并增加对比度
```

### AI Action

```python
result = main(
    photo_path="dark-photo.jpg",
    prompt="Brighten and increase contrast"
)
```

### Output

✅ **Enhanced photo saved**: `dark-photo-enhanced.jpg`

**Photo Analysis**:
- Original brightness: 38/100 - too dark
- Original contrast: 45/100 - low contrast
- Original saturation: 50/100

**GPT-5 Selected Style**: Custom (Bright & Contrast)

**Applied Adjustments**:
- Brightness: ×1.40 (38 → 53) - significant brightening
- Contrast: ×1.35 (45 → 61) - boost contrast
- Saturation: ×1.15 (50 → 58) - slight color boost

**Reasoning**: "Photo is underexposed (brightness 38). Large brightness multiplier (1.4) combined with contrast boost (1.35) improves visibility while maintaining detail."

---

## Error Handling Examples

### API Unavailable

**Scenario**: OpenRouter API timeout

**Fallback Used**:
```
⚠️ API unavailable, using safe defaults
Applied: Brightness ×1.2, Contrast ×1.1, Saturation ×1.2
```

### Multiplier Out of Range

**Scenario**: GPT-5 suggests saturation ×3.5

**Response**:
```
❌ Unsafe multiplier detected: 3.5 > 2.0 max
Clamped to safe maximum: ×2.0
```

### Unsupported Format

**Scenario**: User provides `.webp` file

**Response**:
```
❌ Unsupported format: .webp
Supported formats: JPG, PNG
```

---

## Before/After Comparisons

### Low Light Photo Enhancement

**Before**:
- Brightness: 35
- Contrast: 40
- Saturation: 42

**After** (Dramatic style):
- Brightness: ×1.35 → 47
- Contrast: ×1.55 → 62
- Saturation: ×1.30 → 55

**Result**: Underexposed night photo becomes vibrant, visible cityscape.

### Overexposed Photo Correction

**Before**:
- Brightness: 85
- Contrast: 38
- Saturation: 40

**After** (Natural style):
- Brightness: ×0.88 → 75
- Contrast: ×1.20 → 46
- Saturation: ×1.18 → 47

**Result**: Blown-out sky recovered, details restored in highlights.
