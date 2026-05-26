import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation


def read_csv_rows(file_content: bytes, delimiter: str = ",") -> list[dict]:
    text = file_content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    return [dict(row) for row in reader]


def parse_german_decimal(value: str) -> Decimal | None:
    if value is None or str(value).strip() == "":
        return None
    s = str(value).strip().replace(".", "").replace(",", ".")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def parse_german_date(value: str):
    if not value or not str(value).strip():
        return None
    s = str(value).strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def parse_decimal(value: str) -> Decimal | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        return Decimal(str(value).strip().replace(",", ""))
    except InvalidOperation:
        return None


def normalize_unit(unit: str) -> str:
    if not unit:
        return ""
    u = unit.strip().upper()
    mapping = {
        "KG": "kg",
        "KWH": "kWh",
        "MWH": "MWh",
        "L": "L",
        "M3": "m3",
        "M³": "m3",
        "STK": "each",
    }
    return mapping.get(u, unit.strip())


def convert_to_canonical(value: Decimal, unit: str) -> tuple[Decimal, str]:
    unit = normalize_unit(unit)
    if unit == "MWh":
        return value * Decimal("1000"), "kWh"
    if unit.lower() == "kg":
        return value, "kg"
    return value, unit
