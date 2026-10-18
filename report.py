"""
Скрипт для формирования отчёта по результатам фишинговой кампании.

Читает CSV с результатами рассылки, считает метрики:
- open rate (доля открывших)
- click rate (доля кликнувших)
- report rate (доля пожаловавшихся)

Группирует по отделам и выгружает в Excel с отдельными листами:
- "Сводка" — общие метрики по всей кампании
- "По отделам" — метрики в разрезе отделов
- "Динамика" — пример сравнения с предыдущей кампанией (если передан второй файл)
"""

import sys
from pathlib import Path

import pandas as pd


def load_data(filepath: str) -> pd.DataFrame:
    """Загружает CSV и проверяет наличие нужных колонок."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {filepath}")

    df = pd.read_csv(filepath)

    required = {"employee_id", "department", "opened", "clicked", "reported"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"В файле нет колонок: {missing}")

    return df


def calculate_metrics(df: pd.DataFrame) -> dict:
    """Считает общие метрики по всей кампании."""
    total = len(df)
    return {
        "Всего сотрудников": total,
        "Открыли": int(df["opened"].sum()),
        "Кликнули": int(df["clicked"].sum()),
        "Пожаловались": int(df["reported"].sum()),
        "Open rate, %": round(df["opened"].mean() * 100, 1),
        "Click rate, %": round(df["clicked"].mean() * 100, 1),
        "Report rate, %": round(df["reported"].mean() * 100, 1),
    }


def calculate_by_department(df: pd.DataFrame) -> pd.DataFrame:
    """Считает метрики в разрезе отделов."""
    grouped = df.groupby("department").agg(
        Сотрудников=("employee_id", "count"),
        Открыли=("opened", "sum"),
        Кликнули=("clicked", "sum"),
        Пожаловались=("reported", "sum"),
    ).reset_index()

    grouped["Open rate, %"] = (grouped["Открыли"] / grouped["Сотрудников"] * 100).round(1)
    grouped["Click rate, %"] = (grouped["Кликнули"] / grouped["Сотрудников"] * 100).round(1)
    grouped["Report rate, %"] = (grouped["Пожаловались"] / grouped["Сотрудников"] * 100).round(1)

    # Сортируем по click rate — самые уязвимые отделы сверху
    grouped = grouped.sort_values("Click rate, %", ascending=False)

    return grouped


def compare_with_previous(current: pd.DataFrame, previous: pd.DataFrame) -> pd.DataFrame:
    """Сравнивает текущую кампанию с предыдущей по метрикам."""
    cur_metrics = calculate_metrics(current)
    prev_metrics = calculate_metrics(previous)

    rows = []
    for key in ["Open rate, %", "Click rate, %", "Report rate, %"]:
        rows.append({
            "Метрика": key,
            "Предыдущая кампания": prev_metrics[key],
            "Текущая кампания": cur_metrics[key],
            "Изменение": round(cur_metrics[key] - prev_metrics[key], 1),
        })

    return pd.DataFrame(rows)


def save_report(
    summary: dict,
    by_department: pd.DataFrame,
    output_path: str = "report.xlsx",
    dynamics: pd.DataFrame = None,
):
    """Сохраняет отчёт в Excel с отдельными листами."""
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # Лист 1: сводка
        summary_df = pd.DataFrame(list(summary.items()), columns=["Метрика", "Значение"])
        summary_df.to_excel(writer, sheet_name="Сводка", index=False)

        # Лист 2: по отделам
        by_department.to_excel(writer, sheet_name="По отделам", index=False)

        # Лист 3: динамика (если есть)
        if dynamics is not None:
            dynamics.to_excel(writer, sheet_name="Динамика", index=False)

    print(f"✅ Отчёт сохранён → {output_path}")


def main():
    """Точка входа: читает аргументы командной строки и запускает отчёт."""
    if len(sys.argv) < 2:
        print("Использование: python report.py <campaign_data.csv> [previous_campaign.csv]")
        print("Пример: python report.py campaign_data.csv")
        sys.exit(1)

    current_file = sys.argv[1]
    previous_file = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"📂 Загружаю данные: {current_file}")
    current_df = load_data(current_file)

    print("📊 Считаю метрики...")
    summary = calculate_metrics(current_df)
    by_department = calculate_by_department(current_df)

    dynamics = None
    if previous_file:
        print(f"📈 Сравниваю с предыдущей кампанией: {previous_file}")
        previous_df = load_data(previous_file)
        dynamics = compare_with_previous(current_df, previous_df)

    save_report(summary, by_department, "report.xlsx", dynamics)

    print("\n=== СВОДКА ===")
    for key, value in summary.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
