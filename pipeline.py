from listing_parser import parse_listing_text
from enrichment import enrich_from_listing_text
from location_enrichment import (
    get_golf_enrichment,
    get_beach_enrichment
)
from final_scoring import calculate_final_score

import json
from pathlib import Path
from datetime import datetime


PROPERTIES_FILE = Path("data/properties.json")


def load_properties():
    if not PROPERTIES_FILE.exists():
        return []

    with open(PROPERTIES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_properties(properties):
    PROPERTIES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(PROPERTIES_FILE, "w", encoding="utf-8") as file:
        json.dump(properties, file, indent=2)


def already_saved(properties, address, listing_url):
    for property_record in properties:

        saved_address = property_record.get("address")
        saved_url = property_record.get("listing_url")

        if address and saved_address:
            if address.lower() == saved_address.lower():
                return True

        if listing_url and saved_url:
            if listing_url == saved_url:
                return True

    return False


def analyze_property(listing_text):
    print()
    print("=" * 60)
    print("RETIREMENT HOME FINDER")
    print("=" * 60)

    parsed = parse_listing_text(listing_text)
    listing_enrichment = enrich_from_listing_text(listing_text)

    address = parsed.get("address")

    if not address:
        print("ERROR: Could not determine property address.")
        return None

    print(f"Property: {address}")
    print()
    print("Finding location information...")

    golf = get_golf_enrichment(address)
    beach = get_beach_enrichment(address)

    property_data = {
        **parsed,
        **listing_enrichment,
        **golf,
        **beach,

        "property_type": "single_family",

        # FEMA lookup will be added later.
        "flood_zone": None,
        "flood_risk": "unknown"
    }

    score, category, reasons = calculate_final_score(
        property_data
    )

    record = {
        **property_data,
        "match_score": score,
        "category": category,
        "reasons": reasons,
        "rating": None,
        "date_analyzed": datetime.now().isoformat()
    }

    properties = load_properties()

    duplicate = already_saved(
        properties,
        address,
        parsed.get("listing_url")
    )

    print()
    print("-" * 60)

    if parsed.get("price") is not None:
        print(f"PRICE: ${parsed['price']:,}")

    print(f"BEDS: {parsed.get('bedrooms')}")
    print(f"BATHS: {parsed.get('bathrooms')}")

    if parsed.get("square_feet") is not None:
        print(f"SQ FT: {parsed['square_feet']:,}")

    print()

    if category == "REJECTED":
        print("RESULT: ❌ REJECTED")
    elif category == "TOP MATCH":
        print(f"RESULT: 🟢 {score}% — TOP MATCH")
    elif category == "WORTH CONSIDERING":
        print(
            f"RESULT: 🟡 {score}% — WORTH CONSIDERING"
        )
    else:
        print(f"RESULT: ⚪ {score}% — SAVE ONLY")

    print()
    print("LOCATION")
    print("-" * 60)

    print(
        f"Nearest golf: "
        f"{golf.get('nearest_golf_course')}"
    )

    print(
        f"Golf distance: "
        f"{golf.get('golf_distance_miles')} miles"
    )

    print(
        f"Nearest beach: "
        f"{beach.get('nearest_beach')}"
    )

    print(
        f"Beach distance: "
        f"{beach.get('beach_distance_miles')} miles"
    )

    print()
    print("PROPERTY FEATURES")
    print("-" * 60)

    print(
        f"Single story: "
        f"{parsed.get('single_story')}"
    )

    print(
        f"55+ community: "
        f"{listing_enrichment.get('community_55_plus')}"
    )

    print(
        f"Water view: "
        f"{parsed.get('water_view')}"
    )

    print(
        f"Garage spaces: "
        f"{listing_enrichment.get('garage_spaces')}"
    )

    print(
        f"Fully furnished: "
        f"{parsed.get('fully_furnished')}"
    )

    print(
        f"Amenities: "
        f"{listing_enrichment.get('amenities')}"
    )

    print()
    print("SCORING")
    print("-" * 60)

    for reason in reasons:
        print(f"- {reason}")

    print()

    if duplicate:
        print("Already in database — duplicate not saved.")

    else:
        properties.append(record)
        save_properties(properties)

        print("Property saved to database.")

    return record


if __name__ == "__main__":

    listing = """
    789 Fairway Pond Dr, Murrells Inlet, SC 29576

    $529,900
    3 beds
    2 baths
    2,150 sq ft

    Beautiful single-story move-in ready home
    located in an active adult 55+ golf community.

    Features a two-car garage and gorgeous pond views.

    Residents enjoy a community pool,
    clubhouse, tennis courts and pickleball courts.

    The kitchen and bathrooms have been
    recently renovated.

    Home is fully furnished.

    https://www.example.com/fairway-pond
    """

    analyze_property(listing)
