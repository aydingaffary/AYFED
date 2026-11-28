from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher


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

FUZZY_THRESHOLD = 0.80


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", str(text))
    text = text.translate(DIGIT_MAP).translate(CHAR_MAP)
    text = "".join(c for c in text if c not in BIDI_MARKS)
    # Normalize whitespace inside each line without merging OCR rows.
    return "\n".join(
        " ".join(line.split())
        for line in text.splitlines()
    )


def compact_text(text: str) -> str:
    return "".join(
        char for char in normalize_text(text).casefold()
        if char.isalnum()
    )


def normalize_unit(unit: str) -> str:
    normalized = normalize_text(unit).casefold()
    return re.sub(r"[^a-z0-9/]", "", normalized)


def contains_exact_unit(line: str, expected_unit: str) -> bool:
    normalized_line = normalize_text(line).casefold()
    normalized_unit = normalize_unit(expected_unit)

    if not normalized_unit:
        return False

    pattern = (
        r"(?<![a-z0-9/])"
        + re.escape(normalized_unit)
        + r"(?![a-z0-9/])"
    )

    return re.search(pattern, normalized_line) is not None


def extract_numbers(line: str) -> set[str]:
    normalized = normalize_text(line)

    return set(
        re.findall(
            r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])",
            normalized,
        )
    )


def line_name_score(record: dict, line: str) -> float:
    compact_line = compact_text(line)

    aliases = [
        record.get("test_en", ""),
        record.get("test_fa", ""),
    ]

    best_score = 0.0

    for alias in aliases:
        target = compact_text(alias)

        if not target:
            continue

        if target in compact_line:
            return 1.0

        # Fuzzy matching is restricted to sufficiently long aliases.
        if len(target) < 5 or len(compact_line) < 5:
            continue

        min_length = max(1, len(target) - 1)
        max_length = min(len(compact_line), len(target) + 1)

        for window_size in range(min_length, max_length + 1):
            for start in range(len(compact_line) - window_size + 1):
                candidate = compact_line[start:start + window_size]

                score = SequenceMatcher(
                    None,
                    target,
                    candidate,
                ).ratio()

                best_score = max(best_score, score)

    return best_score if best_score >= FUZZY_THRESHOLD else 0.0


def calculate_record_metrics(
    records: list[dict],
    recognized_text: str,
) -> dict:
    lines = [
        line.strip()
        for line in normalize_text(recognized_text).splitlines()
        if line.strip()
    ]

    # Build candidate record-to-line matches.
    candidates = []

    for record_index, record in enumerate(records):
        for line_index, line in enumerate(lines):
            score = line_name_score(record, line)

            if score > 0:
                candidates.append(
                    (score, record_index, line_index)
                )

    # Greedy one-to-one assignment: each record and line can be
    # assigned at most once.
    candidates.sort(reverse=True)

    assigned_records = {}
    used_lines = set()

    for score, record_index, line_index in candidates:
        if record_index in assigned_records or line_index in used_lines:
            continue

        assigned_records[record_index] = line_index
        used_lines.add(line_index)

    name_correct = len(assigned_records)
    value_correct = 0
    unit_correct = 0
    decimal_total = 0
    decimal_correct = 0
    record_correct = 0

    details = []

    for record_index, record in enumerate(records):
        line_index = assigned_records.get(record_index)
        matched_line = lines[line_index] if line_index is not None else ""

        name_ok = line_index is not None

        expected_value = normalize_text(record["value_text"])
        expected_unit = normalize_unit(record["unit"])

        numbers = extract_numbers(matched_line) if name_ok else set()
        value_ok = expected_value in numbers

        unit_ok = (
            contains_exact_unit(matched_line, record["unit"])
            if name_ok else False
        )

        if value_ok:
            value_correct += 1

        if unit_ok:
            unit_correct += 1

        if "." in expected_value:
            decimal_total += 1
            if value_ok:
                decimal_correct += 1

        complete = name_ok and value_ok and unit_ok

        if complete:
            record_correct += 1

        details.append({
            "test_en": record.get("test_en", ""),
            "matched_line": matched_line,
            "name_correct": name_ok,
            "value_correct": value_ok,
            "unit_correct": unit_ok,
            "record_correct": complete,
        })

    total = len(records)

    return {
        "name_correct": name_correct,
        "name_total": total,
        "name_accuracy": name_correct / total if total else 0.0,

        "value_correct": value_correct,
        "value_total": total,
        "value_accuracy": value_correct / total if total else 0.0,

        # Compatibility with the existing evaluator's terminology.
        "numeric_correct": value_correct,
        "numeric_total": total,
        "numeric_accuracy": value_correct / total if total else 0.0,

        "decimal_correct": decimal_correct,
        "decimal_total": decimal_total,
        "decimal_accuracy": (
            decimal_correct / decimal_total
            if decimal_total else None
        ),

        "unit_correct": unit_correct,
        "unit_total": total,
        "unit_accuracy": unit_correct / total if total else 0.0,

        "record_correct": record_correct,
        "record_total": total,
        "record_accuracy": (
            record_correct / total if total else 0.0
        ),

        "record_details": details,
    }
