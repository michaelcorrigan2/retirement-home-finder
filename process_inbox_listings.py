from email_to_listings import get_unique_listings
from location_enrichment import (
    get_golf_enrichment,
    get_beach_enrichment
)


def process_listings():
    listings = get_unique_listings()

    print()
    print("AUTOMATIC LISTING ENRICHMENT")
    print("=" * 70)

    if not listings:
        print("No listings found.")
        return

    for listing in listings:
        address = listing["address"]

        print()
        print(address)
        print("-" * 70)

        golf = get_golf_enrichment(address)
        beach = get_beach_enrichment(address)

        print(f"Price: ${listing['price']:,}")
        print(f"Beds: {listing['bedrooms']}")
        print(f"Baths: {listing['bathrooms']}")
        print(f"Sq Ft: {listing['square_feet']}")

        print()
        print(
            f"Nearest golf: "
            f"{golf.get('nearest_golf_course')}"
        )
        print(
            f"Golf distance: "
            f"{golf.get('golf_distance_miles')} miles"
        )
        print(
            f"Golf nearby: "
            f"{golf.get('golf_nearby')}"
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
        print("=" * 70)


if __name__ == "__main__":
    process_listings()
