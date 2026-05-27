from .base import convert_to_canonical, parse_german_date, parse_german_decimal, read_csv_rows


def parse_sap_csv(file_content: bytes) -> list[dict]:
    """
    Parse German semicolon SAP ALV-style export.
    Returns list of dicts with keys: raw_data, normalized (or None), errors, row_number.
    """
    rows = read_csv_rows(file_content, delimiter=";")
    results = []

    for idx, row in enumerate(rows, start=2):
        errors = []
        record_type = (row.get("record_type") or row.get("Record_Type") or "").strip().upper()

        if not record_type:
            if row.get("Energieträger") or row.get("Energietraeger"):
                record_type = "FUEL"
            elif row.get("Bestellung") or row.get("Material"):
                record_type = "PROCUREMENT"
            else:
                errors.append("Could not determine record_type")
                results.append({"row_number": idx, "raw_data": row, "normalized": None, "errors": errors})
                continue

        if record_type == "FUEL":
            normalized, row_errors = _parse_fuel(row)
        elif record_type == "PROCUREMENT":
            normalized, row_errors = _parse_procurement(row)
        else:
            row_errors = [f"Unknown record_type: {record_type}"]

        errors.extend(row_errors)
        results.append({
            "row_number": idx,
            "raw_data": row,
            "normalized": normalized,
            "errors": errors,
        })

    return results


def _parse_fuel(row: dict) -> tuple[dict | None, list[str]]:
    errors = []
    fuel_type = (row.get("Energieträger") or row.get("Energietraeger") or "").strip()
    qty = parse_german_decimal(row.get("Verbrauchsmenge") or "")
    unit = (row.get("Mengeneinheit") or "").strip()
    plant = (row.get("Werk") or "").strip()
    cost_center = (row.get("Kostenstelle") or "").strip()
    posting_date = parse_german_date(row.get("Buchungsdatum") or "")

    if qty is None:
        errors.append("Missing fuel quantity (Verbrauchsmenge)")
    if not unit:
        errors.append("Missing unit (Mengeneinheit)")

    quality_flags = []
    activity_value, activity_unit = None, ""
    if qty is not None and unit:
        activity_value, activity_unit = convert_to_canonical(qty, unit)

    return {
        "scope": "SCOPE_1",
        "scope_category": "1.1_stationary_combustion" if "gas" in fuel_type.lower() or "erd" in fuel_type.lower() else "1.2_mobile_combustion",
        "activity_type": f"fuel_{fuel_type.lower().replace(' ', '_')}" if fuel_type else "fuel_unknown",
        "activity_value": activity_value,
        "activity_unit": activity_unit,
        "original_value": qty,
        "original_unit": unit,
        "facility_code": plant,
        "cost_center": cost_center,
        "vendor_id": (row.get("Lieferant") or "").strip(),
        "period_start": posting_date,
        "period_end": posting_date,
        "source_system": "SAP",
        "source_record_id": f"{plant}-{cost_center}-{posting_date}",
        "quality_flags": quality_flags,
        "metadata": {"fuel_type": fuel_type},
    }, errors


def _parse_procurement(row: dict) -> tuple[dict | None, list[str]]:
    errors = []
    qty = parse_german_decimal(row.get("Bestellmenge") or "")
    unit = (row.get("Bestellmengeneinheit") or "").strip()
    netwr = parse_german_decimal(row.get("Nettowert") or "")
    po = (row.get("Bestellung") or "").strip()
    item = (row.get("Position") or "").strip()
    plant = (row.get("Werk") or "").strip()
    order_date = parse_german_date(row.get("Bestelldatum") or row.get("Buchungsdatum") or "")

    quality_flags = []
    if qty is not None and not unit and netwr is None:
        errors.append("Quantity without unit and no spend fallback (Nettowert)")
        quality_flags.append("missing_unit")

    activity_value, activity_unit = None, ""
    if qty is not None and unit:
        activity_value, activity_unit = convert_to_canonical(qty, unit)
    elif netwr is not None:
        activity_value = netwr
        activity_unit = "EUR"
        quality_flags.append("spend_fallback")

    return {
        "scope": "SCOPE_3",
        "scope_category": "3.1_purchased_goods",
        "activity_type": "purchased_goods",
        "activity_value": activity_value,
        "activity_unit": activity_unit,
        "original_value": qty or netwr,
        "original_unit": unit or ((row.get("Währung") or row.get("Waehrung") or "EUR").strip()),
        "facility_code": plant,
        "cost_center": "",
        "vendor_id": (row.get("Lieferant") or "").strip(),
        "period_start": order_date,
        "period_end": order_date,
        "source_system": "SAP",
        "source_record_id": f"{po}-{item}" if po else "",
        "quality_flags": quality_flags,
        "metadata": {
            "material": (row.get("Material") or "").strip(),
            "material_group": (row.get("Warengruppe") or "").strip(),
        },
    }, errors
