import json
from pathlib import Path
from datetime import datetime

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


def score_property(property_data, preferences):
    score = 100
    reasons = []

    profile = preferences["search_profile"]

    if property_data["property_type"] != "single_family":
        return 0, ["Rejected: not a single-family home"]

    if not property_data["single_story"]:
        return 0, ["Rejected: does not have single-story living"]

    if property_data["golf_minutes"] > 15:
        return 0, ["Rejected: too far from golf"]

    price = property_data["price"]

    if 450000 <= price <= 550000:
        reasons.append("Price is within target range")
    elif 550000 < price <= 575000:
        score -= 5
        reasons.append("Slightly above target price")
    elif 575000 < price <= 600000:
        score -= 12
        reasons.append("Above target price")
    else:
        score -= 25
        reasons.append("Price is well outside target range")

    sqft = property_data["square_feet"]

    if 2000 <= sqft <= 2300:
        reasons.append("Square footage is ideal")
    elif 1850 <= sqft <= 2500:
        score -= 5
        reasons.append("Square footage is close to preferred range")
    else:
        score -= 12
        reasons.append("Square footage is outside preferred range")

    if 3 <= property_data["bedrooms"] <= 4:
        reasons.append("Bedroom count fits")
    else:
        score -= 8

    if 2 <= property_data["bathrooms"] <= 3:
        reasons.append("Bathroom count fits")
    else:
        score -= 6

    if property_data["garage_spaces"] >= 2:
        reasons.append("Has preferred 2-car garage")
    else:
        score -= 8

    if property_data["community_55_plus"]:
        reasons.append("55+ community")
    else:
        score -= 7

    if property_data["water_view"]:
        reasons.append("Has water view")
    else:
        score -= 8

    if property_data["beach_minutes"] <= 20:
        reasons.append("Within preferred beach drive")
    elif property_data["beach_minutes"] <= 30:
        score -= 5
    else:
        score -= 10

    if property_data["move_in_ready"]:
        reasons.append("Move-in ready")
    else:
        return 0, ["Rejected: not move-in ready"]

    preferred_amenities = {"pool", "clubhouse", "tennis", "pickleball"}
    amenities = set(property_data["amenities"])
    amenity_matches = len(preferred_amenities.intersection(amenities))

    if amenity_matches >= 3:
        reasons.append("Strong community amenities")
    elif amenity_matches == 2:
        score -= 3
    elif amenity_matches == 1:
        score -= 6
    else:
        score -= 10

    if property_data["fully_furnished"]:
        score += 2
        reasons.append("Fully furnished bonus")

    if property_data["flood_risk"] == "high":
        score -= 10
        reasons.append("Higher flood risk")
    elif property_data["flood_risk"] == "moderate":
        score -= 4

    score = max(0, min(score, 100))

    return score, reasons


def get_match_category(score):
    if score >= 85:
        return "TOP MATCH"
    elif score >= 75:
        return "WORTH CONSIDERING"
    else:
        return "SAVE ONLY"


def property_already_exists(properties, address):
    return any(
        item["address"].lower() == address.lower()
        for item in properties
    )


def save_property(property_data, score, category, reasons):
    properties = load_json(PROPERTIES_FILE, default=[])

    if property_already_exists(properties, property_data["address"]):
        print("Property already saved. Skipping duplicate.")
        return False

    record = {
        **property_data,
        "match_score": score,
        "category": category,
        "reasons": reasons,
        "rating": None,
        "date_analyzed": datetime.now().isoformat()
    }

    properties.append(record)
    save_json(PROPERTIES_FILE, properties)

    return True


def main():
    preferences = load_json(PREFERENCES_FILE)

    sample_property = {
        "address": "123 Example Drive, Murrells Inlet, SC",
        "price": 525000,
        "property_type": "single_family",
        "square_feet": 2150,
        "bedrooms": 3,
        "bathrooms": 2,
        "garage_spaces": 2,
        "single_story": True,
        "community_55_plus": True,
        "golf_minutes": 5,
        "water_view": True,
        "beach_minutes": 18,
        "move_in_ready": True,
        "amenities": [
            "pool",
            "clubhouse",
            "pickleball"
        ],
        "fully_furnished": False,
        "flood_risk": "low"
    }

    score, reasons = score_property(sample_property, preferences)
    category = get_match_category(score)

    print()
    print(sample_property["address"])
    print(f"Match Score: {score}%")
    print(f"Category: {category}")
    print()

    for reason in reasons:
        print("-", reason)

    saved = save_property(
        sample_property,
        score,
        category,
        reasons
    )

    if saved:
        print()
        print("Property saved successfully.")


if __name__ == "__main__":
    main()