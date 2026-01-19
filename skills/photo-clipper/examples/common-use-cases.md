# Photo Clipper Examples

## Example 1: Remove Empty Sky

### User Request

```
帮我裁掉这张照片上方30%的空白天空
```

### AI Action

```python
from photo_clipper import main

result = main(
    photo_path="landscape.jpg",
    prompt="Remove 30% from top to reduce empty sky"
)
```

### Output

✅ **Cropped photo saved**: `landscape-clipped.jpg`

**GPT-5 Analysis**:
- Removed 30% from top
- Kept main subject (mountains) in frame
- Confidence: 0.92

**Reasoning**: "The top 30% contains mostly empty sky with no compositional value. Removing it brings the focus to the mountain range."

---

## Example 2: Focus on Subject

### User Request

```
裁剪照片，聚焦在画面中心的人物
```

### AI Action

```python
result = main(
    photo_path="portrait.jpg",
    prompt="Crop to focus on the person's face in the center"
)
```

### Output

✅ **Cropped photo saved**: `portrait-clipped.jpg`

**GPT-5 Analysis**:
- Removed: 15% top, 20% bottom, 10% left, 10% right
- Focused on central subject
- Confidence: 0.88

**Reasoning**: "The subject is centered but surrounded by empty space. Tight crop improves focus on facial expression."

---

## Example 3: Remove Distractions

### User Request

```
去掉照片左边的树枝
```

### AI Action

```python
result = main(
    photo_path="nature.jpg",
    prompt="Remove the partial tree branch on the left edge"
)
```

### Output

✅ **Cropped photo saved**: `nature-clipped.jpg`

**GPT-5 Analysis**:
- Removed 12% from left
- Preserved main subject on right
- Confidence: 0.95

**Reasoning**: "Tree branch on left edge is distracting. Removing it improves composition without affecting subject."

---

## Example 4: Improve Composition

### User Request

```
应用三分法，优化这张照片的构图
```

### AI Action

```python
result = main(
    photo_path="sunset.jpg",
    prompt="Apply rule of thirds to balance the composition"
)
```

### Output

✅ **Cropped photo saved**: `sunset-clipped.jpg`

**GPT-5 Analysis**:
- Removed: 5% top, 15% bottom, 8% right
- Positioned horizon on upper third line
- Confidence: 0.85

**Reasoning**: "Moving horizon to upper third creates more dynamic balance. Sky is more interesting than foreground."

---

## Example 5: Trim All Edges

### User Request

```
四周各去掉10%，让画面更紧凑
```

### AI Action

```python
result = main(
    photo_path="city.jpg",
    prompt="Remove 10% from all edges for a cleaner frame"
)
```

### Output

✅ **Cropped photo saved**: `city-clipped.jpg`

**GPT-5 Analysis**:
- Removed 10% from all sides
- Maintained aspect ratio
- Confidence: 0.98

**Reasoning**: "Uniform trim removes peripheral distractions while keeping central subject prominent."

---

## Error Handling Examples

### API Unavailable

**Scenario**: OpenRouter API is down

**Fallback**: Returns original photo unchanged

```
⚠️ API unavailable, returning original photo
```

### Unsafe Crop Suggested

**Scenario**: GPT-5 suggests removing 60% from top

**Response**:
```
❌ Unsafe crop detected (60% > 50% max)
Using safe fallback: no crop applied
```

### Invalid File Format

**Scenario**: User provides `.bmp` file

**Response**:
```
❌ Unsupported format: .bmp
Supported formats: JPG, PNG
```
