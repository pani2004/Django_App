from .sap import parse_sap_csv
from .travel import parse_travel_csv
from .utility import parse_utility_csv

PARSERS = {
    "SAP": parse_sap_csv,
    "UTILITY": parse_utility_csv,
    "TRAVEL": parse_travel_csv,
}
