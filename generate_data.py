"""
Генератор тестовых данных для отчёта по фишинговой кампании.
Создаёт CSV с результатами рассылки: кто открыл, кликнул, пожаловался.
"""

import csv
import random
from datetime import datetime, timedelta

# Настройки
NUM_EMPLOYEES = 500
DEPARTMENTS = [
    "Бухгалтерия",
    "IT-отдел",
    "Отдел кадров",
    "Продажи",
    "Маркетинг",
    "Юридический отдел",
    "Служба безопасности",
    "Логистика",
]

# Вероятности по отделам (чем выше, тем уязвимее отдел)
# Это позволяет потом показать в отчёте, что отделы отличаются
DEPARTMENT_RISK = {
    "Бухгалтерия": 0.35,
    "IT-отдел": 0.10,
    "Отдел кадров": 0.25,
    "Продажи": 0.40,
    "Маркетинг": 0.30,
    "Юридический отдел": 0.20,
    "Служба безопасности": 0.05,
    "Логистика": 0.28,
}


def generate_employee_id(index: int) -> str:
    """Генерирует ID сотрудника вида EMP-0001."""
    return f"EMP-{index:04d}"


def generate_data():
    """Генерирует список словарей с данными о рассылке."""
    rows = []
    random.seed(42)  # фиксируем seed, чтобы данные были воспроизводимыми

    for i in range(1, NUM_EMPLOYEES + 1):
        dept = random.choice(DEPARTMENTS)
        risk = DEPARTMENT_RISK[dept]

        # opened: чем выше риск, тем чаще открывают
        opened = 1 if random.random() < (risk + 0.3) else 0
        # clicked: только если открыли, и с вероятностью risk
        clicked = 1 if opened and random.random() < risk else 0
        # reported: чем ниже риск (более зрелый отдел), тем чаще жалуются
        reported = 1 if (1 - risk) * 0.5 > random.random() else 0

        rows.append({
            "employee_id": generate_employee_id(i),
            "department": dept,
            "opened": opened,
            "clicked": clicked,
            "reported": reported,
        })

    return rows


def save_to_csv(rows, filename="campaign_data.csv"):
    """Сохраняет данные в CSV."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["employee_id", "department", "opened", "clicked", "reported"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ Сгенерировано {len(rows)} записей → {filename}")


if __name__ == "__main__":
    data = generate_data()
    save_to_csv(data)
