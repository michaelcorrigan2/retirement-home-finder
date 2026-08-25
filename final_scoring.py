from preference_learning import calculate_preference_adjustments

def calculate_final_score(property_data):
    score = 100
    reasons = []

    if property_data.get("property_type") != "single_family":
        return 0, "REJECTED", ["Not a single-family home"]

    if property_data.get("multi_story") is True:
        return 0, "REJECTED", ["Clear evidence of multi-story living"]

    if property_data.get("move_in_ready") is False:
        return 0, "REJECTED", ["Home does not appear move-in ready"]

    address = (property_data.get("address") or "").lower()

    if "myrtle beach" in address and "north myrtle beach" not in address:
        return 0, "REJECTED", ["Located directly in Myrtle Beach"]

    if property_data.get("backyard_water_view") is not True:
        return 0, "REJECTED", ["No confirmed backyard water view"]

    golf_distance = property_data.get("golf_distance_miles")

    if golf_distance is not None and golf_distance > 8:
        return 0, "REJECTED", ["Too far from golf"]

    price = property_data.get("price")

    if price is not None:
        if 450000 <= price <= 550000:
            reasons.append("Ideal price range")
        elif 550000 < price <= 575000:
            score -= 4
            reasons.append("Slightly above preferred price")
        elif 575000 < price <= 600000:
            score -= 10
            reasons.append("Above preferred price")
        elif 400000 <= price < 450000:
            score -= 2
            reasons.append("Below target price but still reasonable")
        else:
            score -= 18
            reasons.append("Price substantially outside target")

    sqft = property_data.get("square_feet")

    if sqft is not None:
        if 2000 <= sqft <= 2300:
            reasons.append("Ideal square footage")
        elif 1850 <= sqft <= 2500:
            score -= 3
            reasons.append("Square footage close to target")
        elif 1700 <= sqft <= 2700:
            score -= 7
            reasons.append("Square footage outside preferred range")
        else:
            score -= 12
            reasons.append("Square footage well outside preferred range")

    beds = property_data.get("bedrooms")
    if beds is not None and not 3 <= beds <= 4:
        score -= 6
    else:
        reasons.append("Bedroom count fits")

    baths = property_data.get("bathrooms")
    if baths is not None and not 2 <= baths <= 3:
        score -= 4
    else:
        reasons.append("Bathroom count fits")

    garage = property_data.get("garage_spaces")
    if garage is not None and garage >= 2:
        reasons.append("2-car garage")
    else:
        score -= 7
        reasons.append("Garage smaller than preferred or unverified")

    if property_data.get("single_story") is True:
        reasons.append("Single-story living")
    else:
        score -= 8
        reasons.append("Single-story layout not fully verified")

    if property_data.get("community_55_plus") is True:
        score += 4
        reasons.append("55+ community bonus")
    else:
        score -= 4
        reasons.append("Not confirmed as 55+ community")

    reasons.append("Confirmed backyard water view")

    if golf_distance is not None:
        if golf_distance <= 1:
            score += 5
            reasons.append("Excellent golf proximity")
        elif golf_distance <= 3:
            score += 3
            reasons.append("Very close to golf")
        elif golf_distance <= 5:
            reasons.append("Close to golf")
        elif golf_distance <= 8:
            score -= 5
            reasons.append("Golf is somewhat farther away")
    elif property_data.get("golf_mentioned"):
        reasons.append("Golf mentioned in listing")
    else:
        score -= 5
        reasons.append("Golf proximity not verified")

    beach_distance = property_data.get("beach_distance_miles")

    if beach_distance is not None:
        if beach_distance <= 5:
            score += 4
            reasons.append("Excellent beach proximity")
        elif beach_distance <= 10:
            score += 1
            reasons.append("Good beach proximity")
        elif beach_distance <= 15:
            score -= 3
        else:
            score -= 7

    amenities = set(property_data.get("amenities") or [])
    preferred = {"pool", "clubhouse", "tennis", "pickleball"}
    matches = len(amenities.intersection(preferred))

    if matches == 4:
        score += 5
        reasons.append("Excellent community amenities")
    elif matches == 3:
        score += 3
        reasons.append("Strong community amenities")
    elif matches == 2:
        reasons.append("Good community amenities")
    elif matches == 1:
        score -= 3
    else:
        score -= 6

    if property_data.get("fully_furnished") is True:
        score += 2
        reasons.append("Fully furnished bonus")

    if property_data.get("renovated") is True:
        score += 2
        reasons.append("Renovated/updated bonus")

    flood = property_data.get("flood_risk", "unknown")

    if flood == "high":
        score -= 10
        reasons.append("High flood-risk penalty")
    elif flood == "moderate":
        score -= 5
        reasons.append("Moderate flood-risk penalty")


    # ----------------------------
    # LEARNED SOFT PREFERENCES
    # ----------------------------

    learning = calculate_preference_adjustments()

    if learning.get("ready"):
        adjustments = learning.get("adjustments", {})

        for feature, adjustment in adjustments.items():

            if feature.startswith("amenity:"):
                amenity = feature.split(":", 1)[1]

                if amenity in (property_data.get("amenities") or []):
                    score += adjustment

                    reasons.append(
                        f"Learned preference adjustment: "
                        f"{amenity} "
                        f"{'+' if adjustment > 0 else ''}"
                        f"{adjustment}"
                    )

            elif property_data.get(feature) is True:
                score += adjustment

                reasons.append(
                    f"Learned preference adjustment: "
                    f"{feature.replace('_', ' ')} "
                    f"{'+' if adjustment > 0 else ''}"
                    f"{adjustment}"
                )

    score = max(0, min(round(score), 100))

    if score >= 85:
        category = "TOP MATCH"
    elif score >= 75:
        category = "WORTH CONSIDERING"
    else:
        category = "SAVE ONLY"

    return score, category, reasons


if __name__ == "__main__":
    sample = {
        "address": "17 Example Pond Ct, Murrells Inlet, SC 29576",
        "property_type": "single_family",
        "price": 529900,
        "square_feet": 2150,
        "bedrooms": 3,
        "bathrooms": 2,
        "garage_spaces": 2,
        "single_story": True,
        "multi_story": False,
        "move_in_ready": True,
        "community_55_plus": True,
        "water_view": True,
        "backyard_water_view": True,
        "golf_mentioned": True,
        "golf_distance_miles": 0.8,
        "beach_distance_miles": 4.2,
        "amenities": ["pool", "clubhouse", "tennis", "pickleball"],
        "fully_furnished": True,
        "renovated": True,
        "flood_risk": "unknown"
    }

    score, category, reasons = calculate_final_score(sample)

    print()
    print("UPDATED SCORING TEST")
    print("-" * 40)
    print(f"Score: {score}%")
    print(f"Category: {category}")
    print()

    for reason in reasons:
        print("-", reason)
