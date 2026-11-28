from __future__ import annotations

import pytest

from experiments.ocr_benchmark.structured_extraction import (
    calculate_record_metrics,
)


RECORDS = [
    {
        "test_en": "Hemoglobin",
        "test_fa": "هموگلوبین",
        "value": 14.2,
        "value_text": "14.2",
        "unit": "g/dL",
    },
    {
        "test_en": "WBC",
        "test_fa": "گلبول سفید",
        "value": 7200,
        "value_text": "7200",
        "unit": "cells/uL",
    },
    {
        "test_en": "Platelets",
        "test_fa": "پلاکت",
        "value": 250000,
        "value_text": "250000",
        "unit": "cells/uL",
    },
    {
        "test_en": "Fasting Glucose",
        "test_fa": "قند ناشتا",
        "value": 95,
        "value_text": "95",
        "unit": "mg/dL",
    },
]


def test_perfect_english_extraction():
    text = """
    Hemoglobin 14.2 g/dL
    WBC 7200 cells/uL
    Platelets 250000 cells/uL
    Fasting Glucose 95 mg/dL
    """

    metrics = calculate_record_metrics(RECORDS, text)

    assert metrics["name_correct"] == 4
    assert metrics["value_correct"] == 4
    assert metrics["unit_correct"] == 4
    assert metrics["record_correct"] == 4


def test_perfect_persian_extraction():
    text = """
    هموگلوبین ۱۴.۲ g/dL
    گلبول سفید ۷۲۰۰ cells/uL
    پلاکت ۲۵۰۰۰۰ cells/uL
    قند ناشتا ۹۵ mg/dL
    """

    metrics = calculate_record_metrics(RECORDS, text)

    assert metrics["name_correct"] == 4
    assert metrics["value_correct"] == 4
    assert metrics["unit_correct"] == 4
    assert metrics["record_correct"] == 4


def test_swapped_values_must_not_count_as_correct_records():
    text = """
    Hemoglobin 7200 g/dL
    WBC 14.2 cells/uL
    Platelets 250000 cells/uL
    Fasting Glucose 95 mg/dL
    """

    metrics = calculate_record_metrics(RECORDS, text)

    assert metrics["record_correct"] == 2
    assert metrics["value_correct"] == 2


def test_wrong_platelet_value_must_be_rejected():
    text = """
    Hemoglobin 14.2 g/dL
    WBC 7200 cells/uL
    Platelets 20000 cells/uL
    Fasting Glucose 95 mg/dL
    """

    metrics = calculate_record_metrics(RECORDS, text)

    assert metrics["value_correct"] == 3
    assert metrics["record_correct"] == 3


def test_wrong_unit_must_not_count_as_complete_record():
    text = """
    Hemoglobin 14.2 mg/dL
    WBC 7200 cells/uL
    Platelets 250000 cells/uL
    Fasting Glucose 95 mg/dL
    """

    metrics = calculate_record_metrics(RECORDS, text)

    assert metrics["name_correct"] == 4
    assert metrics["value_correct"] == 4
    assert metrics["unit_correct"] == 3
    assert metrics["record_correct"] == 3


def test_value_without_test_name_must_not_count_as_record():
    text = """
    14.2 g/dL
    7200 cells/uL
    250000 cells/uL
    95 mg/dL
    """

    metrics = calculate_record_metrics(RECORDS, text)

    assert metrics["record_correct"] == 0


def test_empty_ocr_output_returns_zero_accuracy():
    metrics = calculate_record_metrics(RECORDS, "")

    assert metrics["name_correct"] == 0
    assert metrics["value_correct"] == 0
    assert metrics["unit_correct"] == 0
    assert metrics["record_correct"] == 0
