from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features


ROOT = Path(__file__).resolve().parent
IMAGE_DIR = ROOT / "dataset" / "images"
GT_DIR = ROOT / "dataset" / "ground_truth"

WIDTH, HEIGHT = 1600, 1100

FONT_EN = "/c/Windows/Fonts/arial.ttf"
FONT_FA = "/c/Windows/Fonts/tahoma.ttf"

if not features.check("raqm"):
    raise RuntimeError("Pillow RAQM support is required for Persian text.")


CASES = [
    {
        "hemoglobin": (14.2, "g/dL"),
        "wbc": (7200, "cells/uL"),
        "platelets": (250000, "cells/uL"),
        "glucose": (95, "mg/dL"),
    },
    {
        "hemoglobin": (13.8, "g/dL"),
        "wbc": (6800, "cells/uL"),
        "platelets": (265000, "cells/uL"),
        "glucose": (102, "mg/dL"),
    },
    {
        "hemoglobin": (15.1, "g/dL"),
        "wbc": (8100, "cells/uL"),
        "platelets": (230000, "cells/uL"),
        "glucose": (88, "mg/dL"),
    },
    {
        "hemoglobin": (12.9, "g/dL"),
        "wbc": (5900, "cells/uL"),
        "platelets": (310000, "cells/uL"),
        "glucose": (110, "mg/dL"),
    },
    {
        "hemoglobin": (14.7, "g/dL"),
        "wbc": (7500, "cells/uL"),
        "platelets": (275000, "cells/uL"),
        "glucose": (99, "mg/dL"),
    },
]

TESTS = [
    ("Hemoglobin", "هموگلوبین", "hemoglobin"),
    ("WBC", "گلبول سفید", "wbc"),
    ("Platelets", "پلاکت", "platelets"),
    ("Fasting Glucose", "قند ناشتا", "glucose"),
]


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def draw_rtl(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    selected_font: ImageFont.FreeTypeFont,
    fill: str = "#111111",
) -> None:
    draw.text(
        position,
        text,
        font=selected_font,
        fill=fill,
        anchor="ra",
        direction="rtl",
        language="fa",
    )


def draw_ltr(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    selected_font: ImageFont.FreeTypeFont,
    fill: str = "#111111",
) -> None:
    draw.text(
        position,
        text,
        font=selected_font,
        fill=fill,
        anchor="la",
    )


def create_report(kind: str, index: int, case: dict) -> dict:
    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)

    title_font = font(FONT_EN, 42)
    heading_font = font(FONT_EN, 28)
    body_font = font(FONT_EN, 25)
    fa_heading_font = font(FONT_FA, 28)
    fa_body_font = font(FONT_FA, 27)
    small_font = font(FONT_EN, 19)

    draw.text((WIDTH // 2, 75), "LABORATORY TEST REPORT",
              font=title_font, fill="#142D4E", anchor="mm")

    draw.text((100, 150), f"Report ID: SYN-{kind.upper()}-{index:02d}",
              font=small_font, fill="#333333")

    draw.text((100, 190), "Patient: Synthetic Test Record",
              font=small_font, fill="#333333")

    draw.text((100, 230), "Date: 2026-11-23",
              font=small_font, fill="#333333")

    draw.line((90, 280, 1510, 280), fill="#333333", width=3)

    rows = []
    for english, persian, key in TESTS:
        value, unit = case[key]
        rows.append({
            "test_en": english,
            "test_fa": persian,
            "value": value,
            "value_text": str(value),
            "unit": unit,
        })

    if kind == "english":
        draw_ltr(draw, (150, 335), "TEST", heading_font)
        draw_ltr(draw, (900, 335), "RESULT", heading_font)
        draw_ltr(draw, (1250, 335), "UNIT", heading_font)

        for row_index, row in enumerate(rows):
            y = 420 + row_index * 125
            draw_ltr(draw, (150, y), row["test_en"], body_font)
            draw_ltr(draw, (900, y), str(row["value"]), body_font)
            draw_ltr(draw, (1250, y), row["unit"], body_font)
            draw.line((120, y + 45, 1480, y + 45),
                      fill="#CCCCCC", width=2)

    elif kind == "persian":
        draw_rtl(draw, (1450, 335), "نام آزمایش", fa_heading_font)
        draw_rtl(draw, (850, 335), "نتیجه", fa_heading_font)
        draw_rtl(draw, (450, 335), "واحد", fa_heading_font)

        for row_index, row in enumerate(rows):
            y = 420 + row_index * 125
            draw_rtl(draw, (1450, y), row["test_fa"], fa_body_font)
            draw.text((850, y), str(row["value"]),
                      font=body_font, fill="#111111", anchor="ra")
            draw.text((450, y), row["unit"],
                      font=small_font, fill="#111111", anchor="ra")
            draw.line((120, y + 45, 1480, y + 45),
                      fill="#CCCCCC", width=2)

    elif kind == "bilingual":
        draw_ltr(draw, (120, 335), "TEST", heading_font)
        draw_rtl(draw, (1050, 335), "نام آزمایش", fa_heading_font)
        draw.text((1250, 335), "RESULT", font=heading_font,
                  fill="#111111", anchor="mm")
        draw.text((1450, 335), "UNIT", font=heading_font,
                  fill="#111111", anchor="mm")

        for row_index, row in enumerate(rows):
            y = 420 + row_index * 125
            draw_ltr(draw, (120, y), row["test_en"], body_font)
            draw_rtl(draw, (1050, y), row["test_fa"], fa_body_font)
            draw.text((1250, y), str(row["value"]),
                      font=body_font, fill="#111111", anchor="mm")
            draw.text((1450, y), row["unit"],
                      font=small_font, fill="#111111", anchor="mm")
            draw.line((100, y + 45, 1500, y + 45),
                      fill="#CCCCCC", width=2)

    else:
        raise ValueError(f"Unknown report type: {kind}")

    draw.text(
        (WIDTH // 2, 1000),
        "SYNTHETIC DATA - NOT A REAL MEDICAL REPORT",
        font=small_font,
        fill="#777777",
        anchor="mm",
    )

    expected_lines = [
        "LABORATORY TEST REPORT",
        f"Report ID: SYN-{kind.upper()}-{index:02d}",
        "Patient: Synthetic Test Record",
        "Date: 2026-11-23",
    ]

    if kind == "english":
        expected_lines.append("TEST | RESULT | UNIT")
        for row in rows:
            expected_lines.append(
                f"{row['test_en']} | {row['value_text']} | {row['unit']}"
            )

    elif kind == "persian":
        expected_lines.append("نام آزمایش | نتیجه | واحد")
        for row in rows:
            expected_lines.append(
                f"{row['test_fa']} | {row['value_text']} | {row['unit']}"
            )

    elif kind == "bilingual":
        expected_lines.append("TEST | نام آزمایش | RESULT | UNIT")
        for row in rows:
            expected_lines.append(
                f"{row['test_en']} | {row['test_fa']} | "
                f"{row['value_text']} | {row['unit']}"
            )

    expected_lines.append(
        "SYNTHETIC DATA - NOT A REAL MEDICAL REPORT"
    )

    expected_text = "\n".join(expected_lines)

    filename = f"{kind}_{index:02d}"
    image_path = IMAGE_DIR / f"{filename}.png"
    gt_path = GT_DIR / f"{filename}.json"

    image.save(image_path, format="PNG")

    ground_truth = {
        "document_id": filename,
        "document_type": kind,
        "synthetic": True,
        "image": f"../images/{filename}.png",
        "language": kind,
        "normalization_profile": {
            "unicode": "NFC",
            "persian_characters": True,
            "normalize_arabic_yeh": True,
            "normalize_arabic_kaf": True,
            "normalize_persian_digits": True,
            "normalize_arabic_indic_digits": True,
            "normalize_whitespace": True,
        },
        "expected_text": expected_text,
        "expected_lines": expected_lines,
        "expected_records": rows,
    }

    gt_path.write_text(
        json.dumps(ground_truth, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return ground_truth


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    GT_DIR.mkdir(parents=True, exist_ok=True)

    generated = []

    for kind in ("english", "persian", "bilingual"):
        for index, case in enumerate(CASES, start=1):
            generated.append(create_report(kind, index, case))

    print(f"Generated images: {len(generated)}")
    print(f"Images directory: {IMAGE_DIR}")
    print(f"Ground truth directory: {GT_DIR}")

    for kind in ("english", "persian", "bilingual"):
        count = sum(item["document_type"] == kind for item in generated)
        print(f"{kind}: {count}")


if __name__ == "__main__":
    main()
