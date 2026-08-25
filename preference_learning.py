from collections import defaultdict

from database import get_all_properties


SOFT_FEATURES = [
    "community_55_plus",
    "fully_furnished",
    "renovated"
]


def get_rated_properties():
    properties = get_all_properties()

    return [
        item
        for item in properties
        if item.get("rating") in {
            "love",
            "maybe",
            "no"
        }
        and item.get("category") != "REJECTED"
    ]


def calculate_preference_adjustments():
    rated = get_rated_properties()

    if len(rated) < 3:
        return {
            "ready": False,
            "rated_count": len(rated),
            "message": (
                "Need at least 3 real rated qualifying homes "
                "before adjusting preferences."
            ),
            "adjustments": {}
        }

    weights = {
        "love": 2,
        "maybe": 1,
        "no": -2
    }

    scores = defaultdict(int)
    counts = defaultdict(int)

    for property_data in rated:
        rating = property_data["rating"]
        rating_weight = weights[rating]

        for feature in SOFT_FEATURES:
            value = property_data.get(feature)

            if value is True:
                scores[feature] += rating_weight
                counts[feature] += 1

        amenities = property_data.get("amenities") or []

        for amenity in amenities:
            key = f"amenity:{amenity}"
            scores[key] += rating_weight
            counts[key] += 1

    adjustments = {}

    for feature, score in scores.items():
        if counts[feature] < 2:
            continue

        if score >= 3:
            adjustments[feature] = 2

        elif score <= -3:
            adjustments[feature] = -2

    return {
        "ready": True,
        "rated_count": len(rated),
        "adjustments": adjustments
    }


if __name__ == "__main__":
    result = calculate_preference_adjustments()

    print()
    print("PREFERENCE LEARNING")
    print("=" * 60)

    print("Rated qualifying homes:", result["rated_count"])
    print("Ready to learn:", result["ready"])

    if not result["ready"]:
        print(result["message"])

    else:
        print("Adjustments:")

        if not result["adjustments"]:
            print("No strong preferences learned yet.")

        for feature, adjustment in result["adjustments"].items():
            print(
                f"- {feature}: "
                f"{'+' if adjustment > 0 else ''}{adjustment} points"
            )
