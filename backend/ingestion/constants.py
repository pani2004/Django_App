"""Prototype emission factor constants — not a production factor library."""

# kg CO2e per kWh — US grid average proxy
GRID_FACTOR_KG_PER_KWH = 0.233

# kg CO2e per hotel night — rough US average proxy
HOTEL_KG_PER_NIGHT = 10.4

# kg CO2e per EUR spend — procurement spend fallback only
SPEND_KG_PER_EUR = 0.45

# Flight: kg CO2e per passenger-km by haul (DEFRA-style proxies)
FLIGHT_FACTORS = {
    "short": {"economy": 0.158, "premium_economy": 0.252, "business": 0.459, "first": 0.592},
    "medium": {"economy": 0.102, "premium_economy": 0.163, "business": 0.296, "first": 0.382},
    "long": {"economy": 0.091, "premium_economy": 0.145, "business": 0.263, "first": 0.340},
}

# Fuel combustion proxies kg CO2e per unit
FUEL_FACTORS = {
    "diesel": {"unit": "L", "factor": 2.68},
    "erdgas": {"unit": "m3", "factor": 2.02},
    "natural_gas": {"unit": "m3", "factor": 2.02},
    "strom": {"unit": "kWh", "factor": 0.233},
    "electricity": {"unit": "kWh", "factor": 0.233},
}

# Ground transport kg CO2e per km
GROUND_FACTOR_KG_PER_KM = 0.171
