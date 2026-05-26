from decimal import Decimal

from .constants import (
    FLIGHT_FACTORS,
    FUEL_FACTORS,
    GRID_FACTOR_KG_PER_KWH,
    GROUND_FACTOR_KG_PER_KM,
    HOTEL_KG_PER_NIGHT,
    SPEND_KG_PER_EUR,
)
from .models import Confidence, EmissionMethod


def estimate_emissions(normalized: dict) -> dict | None:
    """Return emission estimate dict or None if activity cannot be estimated."""
    activity_type = normalized.get("activity_type", "")
    value = normalized.get("activity_value")
    unit = normalized.get("activity_unit", "")
    metadata = normalized.get("metadata") or {}
    quality_flags = normalized.get("quality_flags") or []

    if value is None:
        return None

    value = Decimal(str(value))

    if activity_type == "electricity_kwh" and unit == "kWh":
        kg = value * Decimal(str(GRID_FACTOR_KG_PER_KWH))
        return _result(
            method=EmissionMethod.ACTIVITY,
            factor_source="US grid average proxy (0.233 kg/kWh)",
            factor_value=Decimal(str(GRID_FACTOR_KG_PER_KWH)),
            co2e_kg=kg,
            confidence=Confidence.HIGH,
        )

    if activity_type == "hotel_night":
        kg = value * Decimal(str(HOTEL_KG_PER_NIGHT))
        return _result(
            method=EmissionMethod.ACTIVITY,
            factor_source="Hotel nights proxy (10.4 kg CO2e/night)",
            factor_value=Decimal(str(HOTEL_KG_PER_NIGHT)),
            co2e_kg=kg,
            confidence=Confidence.MEDIUM,
        )

    if activity_type == "flight_segment" and unit == "km":
        haul = _flight_haul(value)
        cabin = (metadata.get("cabin_class") or "economy").lower().replace(" ", "_")
        if "premium" in cabin:
            cabin_key = "premium_economy"
        elif "business" in cabin:
            cabin_key = "business"
        elif "first" in cabin:
            cabin_key = "first"
        else:
            cabin_key = "economy"
        factor = Decimal(str(FLIGHT_FACTORS[haul].get(cabin_key, FLIGHT_FACTORS[haul]["economy"])))
        kg = value * factor
        confidence = Confidence.MEDIUM if "estimated_distance" in quality_flags else Confidence.HIGH
        return _result(
            method=EmissionMethod.DISTANCE if "estimated_distance" in quality_flags else EmissionMethod.ACTIVITY,
            factor_source=f"DEFRA-style proxy {haul} haul {cabin_key}",
            factor_value=factor,
            co2e_kg=kg,
            confidence=confidence,
        )

    if activity_type in ("ground_km", "rail_km") and unit == "km":
        factor = Decimal(str(GROUND_FACTOR_KG_PER_KM))
        kg = value * factor
        conf = Confidence.LOW if "missing_distance" in quality_flags else Confidence.MEDIUM
        return _result(
            method=EmissionMethod.ACTIVITY,
            factor_source="Ground transport proxy (0.171 kg/km)",
            factor_value=factor,
            co2e_kg=kg,
            confidence=conf,
        )

    if activity_type.startswith("fuel_"):
        fuel_key = activity_type.replace("fuel_", "")
        cfg = FUEL_FACTORS.get(fuel_key) or FUEL_FACTORS.get("diesel")
        if unit == cfg["unit"] or (unit == "kWh" and cfg["unit"] == "kWh"):
            factor = Decimal(str(cfg["factor"]))
            kg = value * factor
            return _result(
                method=EmissionMethod.ACTIVITY,
                factor_source=f"Fuel combustion proxy ({fuel_key})",
                factor_value=factor,
                co2e_kg=kg,
                confidence=Confidence.MEDIUM,
            )

    if activity_type == "purchased_goods" and unit == "EUR":
        factor = Decimal(str(SPEND_KG_PER_EUR))
        kg = value * factor
        return _result(
            method=EmissionMethod.SPEND,
            factor_source="Spend-based fallback (0.45 kg CO2e/EUR)",
            factor_value=factor,
            co2e_kg=kg,
            confidence=Confidence.LOW,
        )

    if activity_type == "purchased_goods" and unit == "kg":
        factor = Decimal("1.5")
        kg = value * factor
        return _result(
            method=EmissionMethod.ACTIVITY,
            factor_source="Generic material proxy (1.5 kg CO2e/kg)",
            factor_value=factor,
            co2e_kg=kg,
            confidence=Confidence.MEDIUM,
        )

    return None


def _flight_haul(km: Decimal) -> str:
    if km < 1500:
        return "short"
    if km < 3500:
        return "medium"
    return "long"


def _result(*, method, factor_source, factor_value, co2e_kg, confidence):
    tonnes = co2e_kg / Decimal("1000")
    return {
        "method": method,
        "factor_source": factor_source,
        "factor_value": factor_value,
        "co2e_kg": co2e_kg.quantize(Decimal("0.000001")),
        "co2e_tonnes": tonnes.quantize(Decimal("0.00000001")),
        "confidence": confidence,
    }
