import math

from .base import parse_decimal, read_csv_rows


# Minimal IATA coords for distance estimation (prototype subset)
AIRPORT_COORDS = {
    "SFO": (37.6213, -122.3790),
    "ORD": (41.9742, -87.9073),
    "JFK": (40.6413, -73.7781),
    "LAX": (33.9416, -118.4085),
    "BOS": (42.3656, -71.0096),
}


def parse_travel_csv(file_content: bytes) -> list[dict]:
    rows = read_csv_rows(file_content, delimiter=",")
    results = []

    for idx, row in enumerate(rows, start=2):
        segment = (row.get("segment_type") or "").strip().upper()
        if segment == "AIRFR":
            normalized, errors = _parse_flight(row)
        elif segment == "HOTEL":
            normalized, errors = _parse_hotel(row)
        elif segment in ("CARRT", "RAILF"):
            normalized, errors = _parse_ground(row, segment)
        else:
            normalized, errors = None, [f"Unknown segment_type: {segment}"]

        results.append({
            "row_number": idx,
            "raw_data": row,
            "normalized": normalized,
            "errors": errors,
        })

    return results


def _parse_flight(row: dict) -> tuple[dict | None, list[str]]:
    errors = []
    quality_flags = []
    origin = (row.get("origin_iata") or "").strip().upper()
    dest = (row.get("destination_iata") or "").strip().upper()
    cabin = (row.get("cabin_class") or "Economy").strip()
    trip_id = (row.get("trip_id") or "").strip()
    tx_date = row.get("transaction_date") or ""

    distance = parse_decimal(row.get("distance_km") or "")
    if distance is None and origin and dest:
        distance = _haversine_km(origin, dest)
        if distance:
            quality_flags.append("estimated_distance")
        else:
            errors.append(f"Cannot estimate distance for {origin}-{dest}")

    if not origin or not dest:
        errors.append("Flight missing origin or destination IATA codes")

    return {
        "scope": "SCOPE_3",
        "scope_category": "3.6_business_travel",
        "activity_type": "flight_segment",
        "activity_value": distance,
        "activity_unit": "km",
        "original_value": parse_decimal(row.get("distance_km") or ""),
        "original_unit": "km",
        "facility_code": "",
        "cost_center": (row.get("cost_center") or "").strip(),
        "vendor_id": "",
        "period_start": None,
        "period_end": None,
        "source_system": "TRAVEL",
        "source_record_id": trip_id,
        "quality_flags": quality_flags,
        "metadata": {
            "origin_iata": origin,
            "destination_iata": dest,
            "cabin_class": cabin,
            "transaction_date": tx_date,
        },
    }, errors


def _parse_hotel(row: dict) -> tuple[dict | None, list[str]]:
    errors = []
    nights = parse_decimal(row.get("nights") or "")
    if nights is None:
        errors.append("Hotel row missing nights")

    return {
        "scope": "SCOPE_3",
        "scope_category": "3.6_business_travel",
        "activity_type": "hotel_night",
        "activity_value": nights,
        "activity_unit": "nights",
        "original_value": nights,
        "original_unit": "nights",
        "facility_code": "",
        "cost_center": (row.get("cost_center") or "").strip(),
        "vendor_id": "",
        "period_start": None,
        "period_end": None,
        "source_system": "TRAVEL",
        "source_record_id": (row.get("trip_id") or "").strip(),
        "quality_flags": [],
        "metadata": {
            "city": (row.get("city") or "").strip(),
            "country": (row.get("country") or "").strip(),
        },
    }, errors


def _parse_ground(row: dict, segment: str) -> tuple[dict | None, list[str]]:
    errors = []
    quality_flags = []
    distance = parse_decimal(row.get("distance_km") or "")
    vehicle = (row.get("vehicle_type") or "").strip()

    if distance is None:
        quality_flags.append("missing_distance")
        errors.append("Ground transport missing distance_km")

    activity_type = "rail_km" if segment == "RAILF" else "ground_km"

    return {
        "scope": "SCOPE_3",
        "scope_category": "3.6_business_travel",
        "activity_type": activity_type,
        "activity_value": distance,
        "activity_unit": "km",
        "original_value": distance,
        "original_unit": "km",
        "facility_code": "",
        "cost_center": (row.get("cost_center") or "").strip(),
        "vendor_id": "",
        "period_start": None,
        "period_end": None,
        "source_system": "TRAVEL",
        "source_record_id": (row.get("trip_id") or "").strip(),
        "quality_flags": quality_flags,
        "metadata": {"vehicle_type": vehicle, "segment_type": segment},
    }, errors


def _haversine_km(origin: str, dest: str) -> "Decimal | None":
    from decimal import Decimal

    if origin not in AIRPORT_COORDS or dest not in AIRPORT_COORDS:
        return None
    lat1, lon1 = AIRPORT_COORDS[origin]
    lat2, lon2 = AIRPORT_COORDS[dest]
    r = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return Decimal(str(round(r * c, 2)))
