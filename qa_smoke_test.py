import sys

from database import get_all_properties
from preference_learning import calculate_preference_adjustments
from beach_drive_time import get_beach_drive_enrichment
from final_scoring import calculate_final_score


def check(name, condition):
    if condition:
        print(f"✅ {name}")
        return True

    print(f"❌ {name}")
    return False


def main():
    print()
    print("=" * 65)
    print("RETIREMENT HOME FINDER — V1 QA SMOKE TEST")
    print("=" * 65)

    results = []

    # 1. Database
    properties = get_all_properties()

    results.append(
        check(
            f"Supabase connection ({len(properties)} properties found)",
            isinstance(properties, list)
        )
    )

    # 2. Preference learning
    learning = calculate_preference_adjustments()

    results.append(
        check(
            "Preference-learning module responds",
            isinstance(learning, dict)
            and "rated_count" in learning
        )
    )

    # 3. Real beach routing
    beach = get_beach_drive_enrichment(
        "227 Pin Oak Dr, Murrells Inlet, SC 29576"
    )

    results.append(
        check(
            "Beach drive-time routing",
            beach.get("beach_drive_minutes") is not None
        )
    )

    if beach.get("beach_drive_minutes") is not None:
        print(
            "   Beach:",
            beach.get("nearest_beach_by_drive"),
            "|",
            beach.get("beach_drive_minutes"),
            "minutes"
        )

    # 4. Hard requirement rejection
    bad_house = {
        "address": "QA Bad House",
        "price": 525000,
        "square_feet": 2100,
        "bedrooms": 3,
        "bathrooms": 2,
        "garage_spaces": 2,
        "single_story": False,
        "multi_story": True,
        "move_in_ready": True,
        "backyard_water_view": True,
        "golf_distance_miles": 2,
        "beach_drive_minutes": 10,
        "amenities": [],
        "flood_risk": "unknown"
    }

    score, category, reasons = calculate_final_score(
        bad_house
    )

    results.append(
        check(
            "Multi-story hard rejection",
            score == 0 and category == "REJECTED"
        )
    )

    # 5. Strong qualifying house
    good_house = {
        "address": "QA Good House",
        "property_type": "single_family",
        "price": 525000,
        "square_feet": 2150,
        "bedrooms": 3,
        "bathrooms": 2,
        "garage_spaces": 2,
        "single_story": True,
        "multi_story": False,
        "move_in_ready": True,
        "community_55_plus": True,
        "backyard_water_view": True,
        "water_visual_verified": True,
        "golf_distance_miles": 1.5,
        "golf_mentioned": True,
        "beach_drive_minutes": 15,
        "amenities": [
            "pool",
            "clubhouse",
            "tennis",
            "pickleball"
        ],
        "fully_furnished": False,
        "renovated": True,
        "flood_risk": "unknown"
    }

    score, category, reasons = calculate_final_score(
        good_house
    )

    results.append(
        check(
            f"Qualifying-home scoring ({score}% — {category})",
            score >= 75
            and category in {
                "TOP MATCH",
                "WORTH CONSIDERING"
            }
        )
    )

    print()
    print("=" * 65)

    if all(results):
        print("✅ ALL V1 QA SMOKE TESTS PASSED")
        return 0

    print("❌ ONE OR MORE QA TESTS FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
