from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GT_DIR = ROOT / "dataset" / "ground_truth"
RESULTS_DIR = ROOT / "results"

RAW_RESULTS = RESULTS_DIR / "ocr_raw_results.json"
OUTPUT_JSON = RESULTS_DIR / "ocr_evaluation.json"
OUTPUT_CSV = RESULTS_DIR / "ocr_evaluation.csv"

DIGIT_MAP = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)

CHAR_MAP = str.maketrans({
    "ي": "ی",
    "ى": "ی",
    "ك": "ک",
})

BIDI_MARKS = {
    "\u200e", "\u200f",
    "\u202a", "\u202b", "\u202c",
    "\u202d", "\u202e",
    "\u2066", "\u2067", "\u2068", "\u2069",
}


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.translate(DIGIT_MAP)
    text = text.translate(CHAR_MAP)

    text = "".join(
        char for char in text
        if char not in BIDI_MARKS
    )

    text = text.replace("\u0640", "")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def edit_distance(reference: list, hypothesis: list) -> int:
    previous = list(range(len(hypothesis) + 1))

    for i, ref_item in enumerate(reference, start=1):
        current = [i]

        for j, hyp_item in enumerate(hypothesis, start=1):
            substitution_cost = (
                0 if ref_item == hyp_item else 1
            )

            current.append(min(
                previous[j] + 1,
                current[j - 1] + 1,
                previous[j - 1] + substitution_cost,
            ))

        previous = current

    return previous[-1]


def error_rate(reference: str, hypothesis: str) -> float:
    ref = normalize_text(reference)
    hyp = normalize_text(hypothesis)

    distance = edit_distance(list(ref), list(hyp))

    if not ref:
        return 0.0 if not hyp else 1.0

    return distance / len(ref)


def word_error_rate(reference: str, hypothesis: str) -> float:
    ref = normalize_text(reference).split()
    hyp = normalize_text(hypothesis).split()

    distance = edit_distance(ref, hyp)

    if not ref:
        return 0.0 if not hyp else 1.0

    return distance / len(ref)


def contains_exact_token(text: str, token: str) -> bool:
    normalized_text = normalize_text(text).casefold()
    normalized_token = normalize_text(token).casefold()

    pattern = (
        r"(?<![A-Za-z0-9])"
        + re.escape(normalized_token)
        + r"(?![A-Za-z0-9])"
    )

    return re.search(pattern, normalized_text) is not None


def calculate_record_metrics(
    records: list[dict],
    recognized_text: str,
) -> dict:
    numeric_total = len(records)
    numeric_correct = 0

    decimal_total = 0
    decimal_correct = 0

    unit_total = len(records)
    unit_correct = 0

    for record in records:
        expected_value = record["value_text"]

        if contains_exact_token(recognized_text, expected_value):
            numeric_correct += 1

        if "." in expected_value:
            decimal_total += 1

            if contains_exact_token(
                recognized_text,
                expected_value,
            ):
                decimal_correct += 1

        if contains_exact_token(
            recognized_text,
            record["unit"],
        ):
            unit_correct += 1

    return {
        "numeric_correct": numeric_correct,
        "numeric_total": numeric_total,
        "numeric_accuracy": numeric_correct / numeric_total,
        "decimal_correct": decimal_correct,
        "decimal_total": decimal_total,
        "decimal_accuracy": (
            decimal_correct / decimal_total
            if decimal_total else None
        ),
        "unit_correct": unit_correct,
        "unit_total": unit_total,
        "unit_accuracy": unit_correct / unit_total,
    }


def summarize(rows: list[dict]) -> dict:
    summary = {}

    for key in ("cer", "wer"):
        summary[key] = sum(
            row[key] for row in rows
        ) / len(rows)

    numeric_total = sum(row["numeric_total"] for row in rows)
    numeric_correct = sum(row["numeric_correct"] for row in rows)

    unit_total = sum(row["unit_total"] for row in rows)
    unit_correct = sum(row["unit_correct"] for row in rows)

    decimal_total = sum(row["decimal_total"] for row in rows)
    decimal_correct = sum(row["decimal_correct"] for row in rows)

    summary["numeric_accuracy"] = numeric_correct / numeric_total
    summary["unit_accuracy"] = unit_correct / unit_total
    summary["decimal_accuracy"] = (
        decimal_correct / decimal_total
        if decimal_total else None
    )

    summary["numeric_correct"] = numeric_correct
    summary["numeric_total"] = numeric_total
    summary["decimal_correct"] = decimal_correct
    summary["decimal_total"] = decimal_total
    summary["unit_correct"] = unit_correct
    summary["unit_total"] = unit_total

    summary["average_processing_time_seconds"] = sum(
        row["processing_time_seconds"] for row in rows
    ) / len(rows)

    return summary


def main() -> None:
    raw = json.loads(RAW_RESULTS.read_text(encoding="utf-8"))

    ground_truth = {}

    for path in GT_DIR.glob("*.json"):
        ground_truth[path.stem] = json.loads(
            path.read_text(encoding="utf-8")
        )

    if len(ground_truth) != 15:
        raise RuntimeError(
            f"Expected 15 ground-truth documents, found {len(ground_truth)}"
        )

    if len(raw["results"]) != 45:
        raise RuntimeError(
            f"Expected 45 OCR results, found {len(raw['results'])}"
        )

    rows = []

    for result in raw["results"]:
        document_id = result["document_id"]

        if document_id not in ground_truth:
            raise RuntimeError(
                f"Missing ground truth: {document_id}"
            )

        gt = ground_truth[document_id]
        recognized = result["recognized_text"]
        reference = gt["expected_text"]

        record_metrics = calculate_record_metrics(
            gt["expected_records"],
            recognized,
        )

        rows.append({
            "document_id": document_id,
            "document_type": gt["document_type"],
            "language": result["language"],
            "cer": error_rate(reference, recognized),
            "wer": word_error_rate(reference, recognized),
            **record_metrics,
            "processing_time_seconds": (
                result["processing_time_seconds"]
            ),
        })

    grouped = defaultdict(list)

    for row in rows:
        grouped[
            (row["document_type"], row["language"])
        ].append(row)

    summary = {
        "benchmark": "AYFED OCR Benchmark",
        "dataset_documents": len(ground_truth),
        "total_runs": len(rows),
        "normalization": [
            "NFC",
            "Persian and Arabic digit normalization",
            "Arabic Yeh and Kaf normalization",
            "Bidi control removal",
            "Whitespace normalization",
        ],
        "overall": {},
        "by_document_type_and_language": {},
    }

    for language in sorted({row["language"] for row in rows}):
        selected = [
            row for row in rows
            if row["language"] == language
        ]
        summary["overall"][language] = summarize(selected)

    for (document_type, language), selected in sorted(grouped.items()):
        key = f"{document_type}/{language}"
        summary["by_document_type_and_language"][key] = (
            summarize(selected)
        )

    OUTPUT_JSON.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    fields = list(rows[0].keys())

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("OCR Evaluation Completed")
    print(f"Documents: {len(ground_truth)}")
    print(f"Runs: {len(rows)}")
    print()

    print("OVERALL RESULTS")
    print(
        f"{'Language':<10} {'CER':>10} {'WER':>10} "
        f"{'Numeric':>10} {'Decimal':>10} {'Unit':>10} "
        f"{'Time(s)':>10}"
    )

    for language, metrics in summary["overall"].items():
        decimal = metrics["decimal_accuracy"]

        print(
            f"{language:<10} "
            f"{metrics['cer']:>10.4f} "
            f"{metrics['wer']:>10.4f} "
            f"{metrics['numeric_accuracy']:>9.1%} "
            f"{decimal if decimal is not None else 0:>9.1%} "
            f"{metrics['unit_accuracy']:>9.1%} "
            f"{metrics['average_processing_time_seconds']:>10.3f}"
        )

    print()
    print(f"JSON: {OUTPUT_JSON}")
    print(f"CSV:  {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
