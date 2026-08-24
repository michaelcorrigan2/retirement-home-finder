from email_intake import fetch_listing_emails
from listing_parser import (
    detect_backyard_water_view,
    detect_generic_water_view,
    detect_single_story,
    detect_multi_story,
    detect_move_in_ready,
    detect_fully_furnished
)
from enrichment import (
    detect_garage_spaces,
    detect_55_plus,
    detect_golf,
    detect_amenities,
    detect_renovated
)


def analyze_email_features():
    emails = fetch_listing_emails(limit=50)

    print()
    print("EMAIL FEATURE EXTRACTION")
    print("=" * 70)

    for item in emails:
        text = f"{item['subject']} {item['body']}"

        print()
        print(f"Source: {item['source']}")
        print(f"Subject: {item['subject']}")
        print("-" * 70)

        print(
            "Backyard water view:",
            detect_backyard_water_view(text)
        )
        print(
            "Generic water view:",
            detect_generic_water_view(text)
        )
        print(
            "Single story:",
            detect_single_story(text)
        )
        print(
            "Multi story:",
            detect_multi_story(text)
        )
        print(
            "Move-in ready:",
            detect_move_in_ready(text)
        )
        print(
            "Fully furnished:",
            detect_fully_furnished(text)
        )
        print(
            "Garage spaces:",
            detect_garage_spaces(text)
        )
        print(
            "55+ community:",
            detect_55_plus(text)
        )
        print(
            "Golf mentioned:",
            detect_golf(text)
        )
        print(
            "Amenities:",
            detect_amenities(text)
        )
        print(
            "Renovated:",
            detect_renovated(text)
        )

        print("=" * 70)


if __name__ == "__main__":
    analyze_email_features()
