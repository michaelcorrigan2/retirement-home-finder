import json
from pathlib import Path
from datetime import datetime

from listing_parser import parse_listing_text
from enrichment import enrich_from_listing_text
from location_enrichment import (
    get_golf_enrichment,
    get_beach_enrichment
)


PREFERENCES_FILE = Path("preferences.json")
PROPERTIES_FILE = Path("data/properties.json")


def load_json(path, default=None):
    if not path.exists():
        return default

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def property_already_exists(properties, address=None, listing_url=None):
    for item in properties:
        if address and item.get("address"):
            if item["address"].lower() == address.lower():
                return True

        if listing_url and item.get("listing_url"):
            if item["listing_url"] == listing_url:
                return True

    return False


def save_analysis(record):
    properties = load_json(PROPERTIES_FILE, default=[])

    if property_already_exists(
        properties,
        address=record.get("address"),
        listing_url=record.get("listing_url")
    ):
        print("Property already saved. Skipping duplicate.")
        return False

    properties.append(record)
    save_json(PROPERTIES_FILE, properties)

    print("Property analysis saved.")
    return True


def analyze_listing(text):
    parsed = parse_listing_text(text)
    enriched = enrich_from_listing_text(text)

    address = parsed.get("address")

    golf = get_golf_enrichment(address) if address else {}
    beach = get_beach_enrichment(address) if address else {}

    property_data = {
        **parsed,
        **enriched,
        **golf,
        **beach,
        "property_type": "single_family",
        "flood_risk": "unknown"
    }

    analyzed_at = datetime.now().isoformat()

    if parsed["multi_story"] is True:
        record = {
            **property_data,
            "match_score": 0,
            "category": "REJECTED",
            "rejected": True,
            "rejection_reason": "Clear evidence of multi-story living",
            "reasons": [
                "Rejected: clear evidence of multi-story living"
            ],
            "rating": None,
            "date_analyzed": analyzed_at
        }

        print()
        print("=" * 50)
        print("RETIREMENT HOME ANALYSIS")
        print("=" * 50)
        print(f"Address: {address}")
        print()
        print("RESULT: REJECTED")
        print("Reason: Clear evidence of multi-story living.")

        save_analysis(record)
        return record

    print()
    print("=" * 50)
    print("RETIREMENT HOME ENRICHED ANALYSIS")
    print("=" * 50)

    print(f"Address: {address}")

    if parsed["price"] is not None:
        print(f"Price: ${parsed['price']:,}")

    print(f"Beds: {parsed['bedrooms']}")
    print(f"Baths: {parsed['bathrooms']}")

    if parsed["square_feet"] is not None:
        print(f"Sq Ft: {parsed['square_feet']:,}")

    print()
    print("LISTING FEATURES")
    print("-" * 50)
    print(f"Single story: {parsed['single_story']}")
    print(f"Water view: {parsed['water_view']}")
    print(f"Fully furnished: {parsed['fully_furnished']}")
    print(f"Move-in ready: {parsed['move_in_ready']}")
    print(f"Garage spaces: {enriched['garage_spaces']}")
    print(f"55+ community: {enriched['community_55_plus']}")
    print(f"Amenities: {enriched['amenities']}")
    print(f"Renovated: {enriched['renovated']}")

    print()
    print("LOCATION")
    print("-" * 50)
    print(f"Nearest golf course: {golf.get('nearest_golf_course')}")
    print(f"Golf distance: {golf.get('golf_distance_miles')} miles")
    print(f"Golf nearby: {golf.get('golf_nearby')}")
    print(f"Nearest beach: {beach.get('nearest_beach')}")
    print(f"Beach distance: {beach.get('beach_distance_miles')} miles")
    print(f"Beach nearby: {beach.get('beach_nearby')}")

    print()
    print("STATUS: NEEDS FINAL SCORING")
    print("Flood risk: unknown")

    record = {
        **property_data,
        "match_score": None,
        "category": "PENDING FINAL SCORE",
        "rejected": False,
        "rejection_reason": None,
        "reasons": [],
        "rating": None,
        "date_analyzed": analyzed_at
    }

    save_analysis(record)

    return record


if __name__ == "__main__":
    listing_text = """
    4040 Longleaf Ln, Murrells Inlet, SC 29576

    $510,000
    5 beds
    3 baths
    2,466 sq ft

    Single-family home with a two-car garage.
    Three bedrooms are on the main floor,
    with two additional bedrooms upstairs.

    The home is move-in ready and located near golf.

    https://www.redfin.com/SC/Murrells-Inlet/4040-Longleaf-Ln-29576/home/123880939
    """

    analyze_listing(listing_text)
