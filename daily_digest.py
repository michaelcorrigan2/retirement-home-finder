from datetime import datetime

from database import get_all_properties


def is_today(date_string):
    if not date_string:
        return False

    try:
        analyzed = datetime.fromisoformat(
            date_string.replace("Z", "+00:00")
        )
        return analyzed.date() == datetime.now().date()

    except ValueError:
        return False


def get_listing_url(property_data):
    url = property_data.get("listing_url")

    if url:
        return url

    source_urls = property_data.get("source_urls") or []

    if source_urls:
        return source_urls[0]

    return None


def yes_no_unknown(value):
    if value is True:
        return "Yes"

    if value is False:
        return "No"

    return "Not confirmed"


def format_property(property_data):
    address = property_data.get("address", "Unknown address")
    price = property_data.get("price")
    score = property_data.get("match_score")
    beds = property_data.get("bedrooms")
    baths = property_data.get("bathrooms")
    sqft = property_data.get("square_feet")

    lines = []

    lines.append(f"🏡 {address}")
    lines.append(f"MATCH SCORE: {score}/100")

    details = []

    if price is not None:
        details.append(f"${price:,}")

    if beds is not None:
        details.append(f"{beds} beds")

    if baths is not None:
        details.append(f"{baths:g} baths")

    if sqft is not None:
        details.append(f"{sqft:,} sq ft")

    if details:
        lines.append(" | ".join(details))

    lines.append("")

    lines.append(
        "✅ Backyard water view: "
        + yes_no_unknown(
            property_data.get("backyard_water_view")
        )
    )

    water_type = property_data.get("water_view_type")

    if water_type:
        lines.append(
            f"   Water type: {water_type.title()}"
        )

    lines.append(
        "✅ Single-story: "
        + yes_no_unknown(
            property_data.get("single_story")
        )
    )

    garage = property_data.get("garage_spaces")

    if garage is not None:
        lines.append(
            f"🚗 Garage: {garage}-car"
        )

    golf = property_data.get("nearest_golf_course")
    golf_distance = property_data.get(
        "golf_distance_miles"
    )

    if golf:
        if golf_distance is not None:
            lines.append(
                f"⛳ Golf: {golf} "
                f"({golf_distance} miles)"
            )
        else:
            lines.append(
                f"⛳ Golf: {golf}"
            )

    beach = property_data.get("nearest_beach")
    beach_distance = property_data.get(
        "beach_distance_miles"
    )

    if beach:
        if beach_distance is not None:
            lines.append(
                f"🏖️ Beach: {beach} "
                f"({beach_distance} miles)"
            )
        else:
            lines.append(
                f"🏖️ Beach: {beach}"
            )

    lines.append(
        "🏘️ 55+ community: "
        + yes_no_unknown(
            property_data.get("community_55_plus")
        )
    )

    lines.append(
        "🛋️ Fully furnished: "
        + yes_no_unknown(
            property_data.get("fully_furnished")
        )
    )

    amenities = property_data.get("amenities") or []

    if amenities:
        clean_amenities = [
            str(item).replace("_", " ").title()
            for item in amenities[:6]
        ]

        lines.append(
            "🏊 Amenities: "
            + ", ".join(clean_amenities)
        )

    reasons = property_data.get("reasons") or []

    if reasons:
        lines.append("")
        lines.append("WHY IT MATCHES:")

        for reason in reasons[:6]:
            lines.append(f"• {reason}")

    url = get_listing_url(property_data)

    if url:
        lines.append("")
        lines.append(f"VIEW LISTING: {url}")

    lines.append("")
    lines.append(
        "Rating: ❤️ Love | 🤔 Maybe | ❌ No"
    )

    return "\n".join(lines)


def build_digest():
    properties = get_all_properties()

    todays_properties = [
        property_data
        for property_data in properties
        if is_today(
            property_data.get("date_analyzed")
        )
        and property_data.get("category") in {
            "TOP MATCH",
            "WORTH CONSIDERING"
        }
        and property_data.get(
            "backyard_water_view"
        ) is True
    ]

    top_matches = [
        item
        for item in todays_properties
        if item.get("category") == "TOP MATCH"
    ]

    worth_considering = [
        item
        for item in todays_properties
        if item.get("category")
        == "WORTH CONSIDERING"
    ]

    top_matches.sort(
        key=lambda item: item.get(
            "match_score",
            0
        ),
        reverse=True
    )

    worth_considering.sort(
        key=lambda item: item.get(
            "match_score",
            0
        ),
        reverse=True
    )

    today = datetime.now().strftime(
        "%B %d, %Y"
    )

    lines = [
        "RETIREMENT HOME DAILY DIGEST",
        today,
        "=" * 65,
        ""
    ]

    if (
        not top_matches
        and not worth_considering
    ):
        lines.append(
            "No new homes met all mandatory "
            "requirements and the 75% match "
            "threshold today."
        )

        return "\n".join(lines)

    if top_matches:
        lines.append(
            "🟢 TOP MATCHES — 85%+"
        )
        lines.append("=" * 65)
        lines.append("")

        for item in top_matches:
            lines.append(
                format_property(item)
            )
            lines.append("")
            lines.append("-" * 65)
            lines.append("")

    if worth_considering:
        lines.append(
            "🟡 WORTH CONSIDERING — 75–84%"
        )
        lines.append("=" * 65)
        lines.append("")

        for item in worth_considering:
            lines.append(
                format_property(item)
            )
            lines.append("")
            lines.append("-" * 65)
            lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print()
    print(build_digest())
