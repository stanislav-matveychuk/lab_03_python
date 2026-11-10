"""Обробка показників мікроклімату розумного будинку."""

from __future__ import annotations

import argparse
import configparser
import csv
import json
import sys
from pathlib import Path

import stats_utils as su

THRESHOLDS: dict[str, float] = {
    "temperature": 7.0,
    "humidity": 20.0,
    "pressure": 5000.0,
}
SUPPORTED_STATS = {"average", "min", "max", "median", "jumps"}


def read_csv(filename: Path) -> dict[str, dict[str, float]]:
    """Зчитує CSV та повертає вкладений словник показників."""
    data = {parameter: {} for parameter in THRESHOLDS}
    with filename.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        required = {"timestamp", *THRESHOLDS}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"CSV повинен містити стовпці: {', '.join(sorted(required))}")
        for row_number, row in enumerate(reader, start=2):
            timestamp = (row.get("timestamp") or "").strip()
            if not timestamp:
                raise ValueError(f"Рядок {row_number}: відсутня часова мітка")
            for parameter in THRESHOLDS:
                try:
                    data[parameter][timestamp] = float(row[parameter])
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        f"Рядок {row_number}: некоректне значення {parameter}"
                    ) from error
    if not any(data.values()):
        raise ValueError("CSV не містить вимірювань")
    return data


def read_config(filename: Path) -> dict[str, list[str]]:
    """Зчитує INI та повертає статистики для кожного показника."""
    parser = configparser.ConfigParser()
    with filename.open("r", encoding="utf-8") as file:
        parser.read_file(file)
    config: dict[str, list[str]] = {}
    for parameter in THRESHOLDS:
        if not parser.has_section(parameter):
            continue
        stats = [item.strip().lower() for item in parser.get(parameter, "stats").split(",")]
        unknown = set(stats) - SUPPORTED_STATS
        if unknown:
            raise ValueError(f"Невідомі статистики для {parameter}: {', '.join(sorted(unknown))}")
        config[parameter] = stats
    if not config:
        raise ValueError("У конфігурації немає підтримуваних розділів")
    return config


def calculate_statistics(
    parameter: str, readings: dict[str, float], requested: list[str]
) -> dict[str, object]:
    """Обчислює характеристики, вказані в конфігурації."""
    timestamps = list(readings)
    values = list(readings.values())
    functions = {
        "average": lambda: su.get_average(values),
        "min": lambda: su.get_min(values),
        "max": lambda: su.get_max(values),
        "median": lambda: su.get_median(values),
        "jumps": lambda: su.detect_jumps(values, timestamps, THRESHOLDS[parameter]),
    }
    return {name: functions[name]() for name in requested}


def parse_arguments() -> argparse.Namespace:
    """Зчитує назви вхідних і вихідного файлів із командного рядка."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data.csv"))
    parser.add_argument("--config", type=Path, default=Path("config.ini"))
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    return parser.parse_args()


def main() -> int:
    """Керує зчитуванням, обробкою, виведенням і збереженням даних."""
    args = parse_arguments()
    try:
        data = read_csv(args.data)
        config = read_config(args.config)
        results: dict[str, dict[str, object]] = {}
        for parameter, requested_stats in config.items():
            su.print_table(parameter, data[parameter])
            results[parameter] = calculate_statistics(
                parameter, data[parameter], requested_stats
            )
            su.print_results(parameter, results[parameter])
        with args.output.open("w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
        print(f"\nРезультати збережено у файлі {args.output}")
        return 0
    except (FileNotFoundError, PermissionError, ValueError, configparser.Error, OSError) as error:
        print(f"Помилка: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
