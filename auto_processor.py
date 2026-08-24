import json
from pathlib import Path
from datetime import datetime

from email_to_listings import get_unique_listings
from property_research import research_property
from location_enrichment import (
    get_golf_enrichment,
    get_beach_enrichment
)
from final_scoring import calculate_final_score


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


def normalize_address(address):
    return "".join(
        character.lower()
        for character in address
        if character.isalnum()
    )


def already_processed(properties, address):
    target = normalize_address(address)

    for property_data in properties:
        saved_address = property_data.get("address")

        if saved_address:
            if normalize_address(saved_address) == target:
                return True

    return False


def cheap_prescreen(listing):
    price = listing.get("price")
    beds = listing.get("bedrooms")
    baths = listing.get("bathrooms")
    sqft = listing.get("square_feet")

    reasons = []

    # Avoid paying for web research on obviously bad listings.
    if price is not None and price > 625000:
        reasons.append("Price too high")

    if beds is not None and beds < 3:
        reasons.append("Fewer than 3 bedrooms")

    if baths is not None and baths < 2:
        reasons.append("Fewer than 2 bathrooms")

    if sqft is not None and sqft < 1600:
        reasons.append("Too small")

    return reasons


def process_inbox():
    listings = get_unique_listings()
    properties = load_properties()

    print()
    print("=" * 70)
    print("AUTOMATIC RETIREMENT HOME PROCESSOR")
    print("=" * 70)

    for listing in listings:
        address = listing["address"]

        print()
        print(address)
        print("-" * 70)

        if already_processed(properties, address):
            print("Already processed — skipping.")
            continue

        prescreen_reasons = cheap_prescreen(listing)

        if prescreen_reasons:
            record = {
                **listing,
                "category": "REJECTED",
                "match_score": 0,
                "rejected": True,
                "rejection_reason": "; ".join(prescreen_reasons),
                "date_analyzed": datetime.now().isoformat()
            }

            properties.append(record)

            print("REJECTED BEFORE WEB RESEARCH")
            print("; ".join(prescreen_reasons))
            continue

        print("Researching property...")

        try:
            research = research_property(address)
        except Exception as error:
            print(f"Research failed: {error}")
            continue

        # Mandatory backyard water rule
        if research.get("backyard_water_view") is not True:
            record = {
                **listing,
                **research,
                "category": "REJECTED",
                "match_score": 0,
                "rejected": True,
                "rejection_reason": "No confirmed backyard water view",
                "date_analyzed": datetime.now().isoformat()
            }

            properties.append(record)

            print("RESULT: REJECTED")
            print("Reason: No confirmed backyard water view")
            continue

        # Mandatory single-story rule
        if research.get("single_story") is not True:
            record = {
                **listing,
                **research,
                "category": "REJECTED",
                "match_score": 0,
                "rejected": True,
                "rejection_reason": "Not confirmed as single-story living",
                "date_analyzed": datetime.now().isoformat()
            }

            properties.append(record)

            print("RESULT: REJECTED")
            print("Reason: Not confirmed as single-story living")
            continue

        print("Mandatory requirements passed.")
        print("Finding golf and beach proximity...")

        golf = get_golf_enrichment(address)
        beach = get_beach_enrichment(address)

        property_data = {
            **listing,
            **research,
            **golf,
            **beach,

            "property_type": "single_family",
            "multi_story": (
                False
                if research.get("single_story") is True
                else None
            ),

            "golf_mentioned": (
                research.get("garage_spaces") is not None
            ),

            "flood_risk": "unknown"
        }

        score, category, reasons = calculate_final_score(
            property_data
        )

        record = {
            **property_data,
            "match_score": score,
            "category": category,
            "rejected": category == "REJECTED",
            "reasons": reasons,
            "rating": None,
            "date_analyzed": datetime.now().isoformat()
        }

        properties.append(record)

        print()
        print(f"RESULT: {score}% — {category}")

        print(
            f"Backyard water: "
            f"{research.get('backyard_water_view')}"
        )

        print(
            f"Water type: "
            f"{research.get('water_view_type')}"
        )

        print(
            f"Single story: "
            f"{research.get('single_story')}"
        )

        print(
            f"Nearest golf: "
            f"{golf.get('nearest_golf_course')}"
        )

        print(
            f"Golf distance: "
            f"{golf.get('golf_distance_miles')} miles"
        )

        print(
            f"Beach distance: "
            f"{beach.get('beach_distance_miles')} miles"
        )

    save_properties(properties)

    print()
    print("Processing complete.")
    print("=" * 70)


if __name__ == "__main__":
    process_inbox()
