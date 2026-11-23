from __future__ import annotations

import json
import time
from pathlib import Path

import pytesseract
from PIL import Image


ROOT = Path(__file__).resolve().parent
DATASET_DIR = ROOT / "dataset"
IMAGE_DIR = DATASET_DIR / "images"
GT_DIR = DATASET_DIR / "ground_truth"
RESULTS_DIR = ROOT / "results"

LANGUAGES = ("eng", "fas", "fas+eng")
OCR_CONFIG = "--oem 1 --psm 6"


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    documents = sorted(GT_DIR.glob("*.json"))
    if len(documents) != 15:
        raise RuntimeError(
            f"Expected 15 ground-truth files, found {len(documents)}"
        )

    version = str(pytesseract.get_tesseract_version())
    available_languages = set(
        pytesseract.get_languages(config="")
    )

    required_languages = {"eng", "fas"}
    missing = required_languages - available_languages

    if missing:
        raise RuntimeError(
            f"Missing Tesseract languages: {sorted(missing)}"
        )

    results = []

    for gt_path in documents:
        ground_truth = json.loads(
            gt_path.read_text(encoding="utf-8")
        )

        image_path = IMAGE_DIR / f"{gt_path.stem}.png"

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        with Image.open(image_path) as image:
            image = image.convert("RGB")

            for language in LANGUAGES:
                started = time.perf_counter()

                text = pytesseract.image_to_string(
                    image,
                    lang=language,
                    config=OCR_CONFIG,
                )

                elapsed = time.perf_counter() - started

                results.append({
                    "document_id": ground_truth["document_id"],
                    "document_type": ground_truth["document_type"],
                    "language": language,
                    "ocr_config": OCR_CONFIG,
                    "engine_version": version,
                    "processing_time_seconds": round(elapsed, 6),
                    "recognized_text": text,
                })

                print(
                    f"{ground_truth['document_id']} | "
                    f"{language:7s} | "
                    f"{elapsed:.3f}s | "
                    f"{len(text)} characters"
                )

    output = {
        "benchmark": "AYFED OCR Benchmark",
        "synthetic_dataset": True,
        "document_count": len(documents),
        "language_configurations": list(LANGUAGES),
        "total_runs": len(results),
        "tesseract_version": version,
        "ocr_config": OCR_CONFIG,
        "results": results,
    }

    output_path = RESULTS_DIR / "ocr_raw_results.json"

    output_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print()
    print(f"Total OCR runs: {len(results)}")
    print(f"Results saved: {output_path}")


if __name__ == "__main__":
    main()
