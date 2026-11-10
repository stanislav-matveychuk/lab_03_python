"""Статистичні функції для обробки показників мікроклімату."""

from __future__ import annotations

import statistics
from collections.abc import Mapping, Sequence


def get_average(values: Sequence[float]) -> float | None:
    """Повертає середнє значення, округлене до двох знаків."""
    return round(statistics.mean(values), 2) if values else None


def get_min(values: Sequence[float]) -> float | None:
    """Повертає мінімальне значення."""
    return min(values) if values else None


def get_max(values: Sequence[float]) -> float | None:
    """Повертає максимальне значення."""
    return max(values) if values else None


def get_median(values: Sequence[float]) -> float | None:
    """Повертає медіану, округлену до двох знаків."""
    return round(statistics.median(values), 2) if values else None


def detect_jumps(
    values: Sequence[float], timestamps: Sequence[str], threshold: float
) -> list[str]:
    """Повертає часові мітки перепадів, більших за threshold."""
    if len(values) != len(timestamps):
        raise ValueError("Кількість значень і часових міток не збігається")
    return [
        timestamps[index]
        for index in range(1, len(values))
        if abs(values[index] - values[index - 1]) > threshold
    ]


def print_table(parameter_name: str, data_dict: Mapping[str, float]) -> None:
    """Виводить початкові значення показника у вигляді таблиці."""
    value_width = max(11, len(parameter_name))
    border = f"+------------------+-{'-' * value_width}-+"
    print(f"\nПоказники для параметра: {parameter_name}")
    print(border)
    print(f"| {'Timestamp':<16} | {parameter_name:<{value_width}} |")
    print(border)
    for timestamp, value in data_dict.items():
        print(f"| {timestamp:<16} | {value:<{value_width}g} |")
    print(border)


def print_results(parameter_name: str, results: Mapping[str, object]) -> None:
    """Виводить розраховані характеристики показника."""
    print(f"\nРезультати для {parameter_name}:")
    for statistic_name, value in results.items():
        print(f"  {statistic_name}: {value}")
