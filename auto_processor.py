from datetime import datetime

from search_areas import location_allowed

from email_to_listings import get_unique_listings
from property_research import research_property
from location_enrichment import (
    get_golf_enrichment,
    get_beach_enrichment
)
from final_scoring import calculate_final_score
from beach_drive_time import get_beach_drive_enrichment
from database import property_exists, save_property


def cheap_prescreen(listing):
    reasons = []

    price = listing.get("price")
    beds = listing.get("bedrooms")
    baths = listing.get("bathrooms")
    sqft = listing.get("square_feet")

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

    print()
    print("=" * 70)
    print("AUTOMATIC RETIREMENT HOME PROCESSOR")
    print("=" * 70)

    for listing in listings:
        address = listing["address"]

        print()
        print(address)
        print("-" * 70)

        if not location_allowed(address):
            print("Outside approved search area — skipping.")
            continue

        if property_exists(address):
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

            save_property(record)

            print("REJECTED BEFORE WEB RESEARCH")
            print("; ".join(prescreen_reasons))
            continue

        print("Researching property...")

        try:
            research = research_property(address)
        except Exception as error:
            print(f"Research failed: {error}")
            continue

        water_evidence = research.get("backyard_water_view")

        if water_evidence is not True:
            record = {
                **listing,
                **research,
                "category": "REJECTED",
                "match_score": 0,
                "rejected": True,
                "water_visual_verified": False,
                "rejection_reason": "No convincing backyard water-view evidence",
                "date_analyzed": datetime.now().isoformat()
            }

            save_property(record)

            print("RESULT: REJECTED")
            print("Reason: No convincing backyard water-view evidence")
            continue

        record = {
            **listing,
            **research,
            "category": "PENDING WATER REVIEW",
            "match_score": None,
            "rejected": False,
            "water_visual_verified": False,
            "rejection_reason": None,
            "date_analyzed": datetime.now().isoformat()
        }

        save_property(record)

        print("RESULT: PENDING WATER REVIEW")
        print(
            "Reason: Listing text suggests a rear water view, "
            "but photos must confirm it."
        )
        continue

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

            save_property(record)

            print("RESULT: REJECTED")
            print("Reason: Not confirmed as single-story living")
            continue

        print("Mandatory requirements passed.")
        print("Finding golf and beach proximity...")

        golf = get_golf_enrichment(address)
        beach = get_beach_enrichment(address)
        beach_drive = get_beach_drive_enrichment(address)

        property_data = {
            **listing,
            **research,
            **golf,
            **beach,
            **beach_drive,
            "property_type": "single_family",
            "multi_story": (
                False if research.get("single_story") is True else None
            ),
            "golf_mentioned": True if golf.get("nearest_golf_course") else False,
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

        save_property(record)

        print()
        print(f"RESULT: {score}% — {category}")
        print(f"Backyard water: {research.get('backyard_water_view')}")
        print(f"Water type: {research.get('water_view_type')}")
        print(f"Single story: {research.get('single_story')}")
        print(f"Nearest golf: {golf.get('nearest_golf_course')}")
        print(f"Golf distance: {golf.get('golf_distance_miles')} miles")
        print(f"Beach distance: {beach.get('beach_distance_miles')} miles")

    print()
    print("Processing complete.")
    print("=" * 70)


if __name__ == "__main__":
    process_inbox()
