import json

# ✅ Analyze ONE canvas JSON
def analyze_image_with_json(overlay_path, canvas_json_str):
    try:
        canvas_data = json.loads(canvas_json_str)
        objects = canvas_data.get('objects', [])
    except Exception:
        return "❌ Invalid canvas data"

    drawing_count = 0
    rect_count = 0
    text_count = 0
    number_count = 0
    valid_numbers = {round(i * 0.5, 1) for i in range(0, 13)}  # 0 to 6.0 in steps of 0.5

    for obj in objects:
        obj_type = obj.get('type', '')
        if obj_type == 'path':
            drawing_count += 1
        elif obj_type == 'rect':
            rect_count += 1
        elif obj_type in ['i-text', 'textbox', 'text']:
            raw_text = obj.get('text', '').strip()
            if raw_text:
                try:
                    num = round(float(raw_text), 1)
                    if num in valid_numbers:
                        number_count += 1
                    else:
                        text_count += 1
                except ValueError:
                    text_count += 1

    result = []
    if drawing_count > 0:
        result.append(f"🖍️ Drawing ({drawing_count})")
    if rect_count > 0:
        result.append(f"🟦 Rectangle ({rect_count})")
    if text_count > 0:
        result.append(f"🔤 Text ({text_count})")
    if number_count > 0:
        result.append(f"🔢 Number Tags ({number_count})")

    return "Detected: " + ", ".join(result) if result else "❌ No clear annotation found"


# ✅ Analyze MULTIPLE canvas JSONs with per-image + total summary
def analyze_multiple_canvas_jsons(canvas_json_list):
    total_drawing = 0
    total_rect = 0
    total_text = 0
    total_number_tags = 0
    total_number_score = 0.0
    valid_numbers = {round(i * 0.5, 1) for i in range(0, 13)}

    result_lines = []

    for idx, canvas_json_str in enumerate(canvas_json_list, start=1):
        try:
            canvas_data = json.loads(canvas_json_str)
            objects = canvas_data.get('objects', [])
        except Exception:
            result_lines.append(f"🖼️ Image {idx}: ❌ Invalid JSON")
            continue

        drawing_count = 0
        rect_count = 0
        text_count = 0
        number_texts = []
        image_number_score = 0.0
        image_number_count = 0
        text_count = 0

        for obj in objects:
            obj_type = obj.get('type', '')
            if obj_type == 'path':
                drawing_count += 1
            elif obj_type == 'rect':
                rect_count += 1
            elif obj_type in ['i-text', 'textbox', 'text']:
                raw_text = obj.get('text', '').strip()
                if raw_text:
                    try:
                        num = round(float(raw_text), 1)
                        if num in valid_numbers:
                            image_number_score += num
                            number_texts.append(str(num))
                            image_number_count += 1
                        else:
                            text_count += 1
                    except ValueError:
                        text_count += 1

        # Add to totals
        total_drawing += drawing_count
        total_rect += rect_count
        total_text += text_count
        total_number_tags += image_number_count
        total_number_score += image_number_score

        # Per-image result
        parts = []
        if drawing_count: parts.append(f"🖍️ {drawing_count} Drawings")
        if rect_count:    parts.append(f"🟦 {rect_count} Rectangles")
        if text_count:    parts.append(f"🔤 {text_count} Texts")
        if image_number_count:
            number_str = ", ".join(number_texts)
            parts.append(f"#⃣ {image_number_count} Numbers ({number_str})")
        if parts:
            result_lines.append(f"🖼️ Image {idx}: " + ", ".join(parts))
        else:
            result_lines.append(f"🖼️ Image {idx}: ❌ No annotations found")

    # Total summary
    result_lines.append("\n📊 Total Summary:")
    total_parts = []
    if total_drawing: total_parts.append(f"🖍️ {total_drawing} Drawings")
    if total_rect:    total_parts.append(f"🟦 {total_rect} Rectangles")
    if total_text:    total_parts.append(f"🔤 {total_text} Texts")
    if total_number_tags:
        total_parts.append(f"#⃣ {total_number_tags} Number Tags (Total Marks: {total_number_score})")
    else:
        total_parts.append("❌ No numbers tagged")

    result_lines.append(" + ".join(total_parts))

    return "\n".join(result_lines)
