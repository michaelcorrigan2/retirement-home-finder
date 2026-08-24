import json
from pathlib import Path
from datetime import datetime

PROPERTIES_FILE = Path("data/properties.json")


def load_properties():
    if not PROPERTIES_FILE.exists():
        return []

    with open(PROPERTIES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def is_today(date_string):
    if not date_string:
        return False

    try:
        analyzed = datetime.fromisoformat(date_string)
        return analyzed.date() == datetime.now().date()
    except ValueError:
        return False


def format_property(property_data):
    address = property_data.get("address", "Unknown address")
    price = property_data.get("price")
    score = property_data.get("match_score")
    category = property_data.get("category")
    beds = property_data.get("bedrooms")
    baths = property_data.get("bathrooms")
    sqft = property_data.get("square_feet")
    url = property_data.get("listing_url")

    lines = []

    lines.append(f"{score}% MATCH — {address}")

    if price is not None:
        lines.append(f"${price:,}")

    details = []

    if beds is not None:
        details.append(f"{beds} beds")

    if baths is not None:
        details.append(f"{baths} baths")

    if sqft is not None:
        details.append(f"{sqft:,} sq ft")

    if details:
        lines.append(" | ".join(details))

    water = property_data.get("backyard_water_view")
    golf = property_data.get("nearest_golf_course")
    golf_distance = property_data.get("golf_distance_miles")
    furnished = property_data.get("fully_furnished")
    community_55 = property_data.get("community_55_plus")

    lines.append(
        f"Backyard water view: {'Yes' if water else 'Not confirmed'}"
    )

    if golf:
        if golf_distance is not None:
            lines.append(
                f"Golf: {golf} ({golf_distance} miles)"
            )
        else:
            lines.append(f"Golf: {golf}")

    lines.append(
        f"55+ community: {'Yes' if community_55 else 'Not confirmed'}"
    )

    lines.append(
        f"Fully furnished: {'Yes' if furnished else 'No'}"
    )

    if url:
        lines.append(f"Listing: {url}")

    lines.append("Rating: ❤️ Love | 🤔 Maybe | ❌ No")

    return "\n".join(lines)


def build_digest():
    properties = load_properties()

    todays_properties = [
        property_data
        for property_data in properties
        if is_today(property_data.get("date_analyzed"))
        and property_data.get("category") in {
            "TOP MATCH",
            "WORTH CONSIDERING"
        }
        and property_data.get("backyard_water_view") is True
    ]

    top_matches = [
        property_data
        for property_data in todays_properties
        if property_data.get("category") == "TOP MATCH"
    ]

    worth_considering = [
        property_data
        for property_data in todays_properties
        if property_data.get("category") == "WORTH CONSIDERING"
    ]

    top_matches.sort(
        key=lambda item: item.get("match_score", 0),
        reverse=True
    )

    worth_considering.sort(
        key=lambda item: item.get("match_score", 0),
        reverse=True
    )

    today = datetime.now().strftime("%B %d, %Y")

    lines = []

    lines.append("RETIREMENT HOME DAILY DIGEST")
    lines.append(today)
    lines.append("=" * 60)
    lines.append("")

    if not top_matches and not worth_considering:
        lines.append(
            "No new homes met the 75% match threshold today."
        )
        return "\n".join(lines)

    if top_matches:
        lines.append("🟢 TOP MATCHES — 85%+")
        lines.append("-" * 60)

        for property_data in top_matches:
            lines.append(format_property(property_data))
            lines.append("")
            lines.append("-" * 60)
            lines.append("")

    if worth_considering:
        lines.append("🟡 WORTH CONSIDERING — 75–84%")
        lines.append("-" * 60)

        for property_data in worth_considering:
            lines.append(format_property(property_data))
            lines.append("")
            lines.append("-" * 60)
            lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    digest = build_digest()

    print()
    print(digest)
