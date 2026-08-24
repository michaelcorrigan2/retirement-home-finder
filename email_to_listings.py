import re

from email_intake import fetch_listing_emails


SUPPORTED_CITIES = (
    "Murrells Inlet",
    "North Myrtle Beach",
    "Surfside Beach",
    "Garden City",
    "Pawleys Island",
    "Little River"
)


def parse_realtor_email(body):
    listings = []

    city_pattern = "|".join(
        re.escape(city) for city in SUPPORTED_CITIES
    )

    pattern = re.compile(
        rf"For sale\s*"
        rf"\$([\d,]+)\s*"
        rf"(\d+)\s*bed\s*"
        rf"(\d+(?:\.\d+)?)\s*bath\s*"
        rf"([\d,]+)\s*sqft\s*"
        rf"(.+?)\s+"
        rf"({city_pattern}),\s*SC\s*(\d{{5}})",
        re.IGNORECASE
    )

    for match in pattern.finditer(body):
        price = int(match.group(1).replace(",", ""))
        beds = int(match.group(2))
        baths = float(match.group(3))
        sqft = int(match.group(4).replace(",", ""))

        street = match.group(5).strip()
        city = match.group(6).strip()
        zipcode = match.group(7)

        address = f"{street}, {city}, SC {zipcode}"

        listings.append({
            "source": "Realtor.com",
            "address": address,
            "price": price,
            "bedrooms": beds,
            "bathrooms": baths,
            "square_feet": sqft,
            "raw_text": match.group(0)
        })

    return listings


def parse_zillow_email(subject, body):
    listings = []

    city_pattern = "|".join(
        re.escape(city) for city in SUPPORTED_CITIES
    )

    address_match = re.search(
        rf"New Listing:\s*"
        rf"(.+?),\s*"
        rf"({city_pattern}),\s*SC\s*(\d{{5}})",
        subject,
        re.IGNORECASE
    )

    price_match = re.search(
        r"New listing for sale at \$([\d,]+)",
        body,
        re.IGNORECASE
    )

    if not address_match or not price_match:
        return []

    street = address_match.group(1).strip().rstrip(".")
    city = address_match.group(2)
    zipcode = address_match.group(3)

    address = f"{street}, {city}, SC {zipcode}"

    price = int(
        price_match.group(1).replace(",", "")
    )

    listings.append({
        "source": "Zillow",
        "address": address,
        "price": price,
        "bedrooms": None,
        "bathrooms": None,
        "square_feet": None,
        "raw_text": f"{subject} {body}"
    })

    return listings


def extract_listings_from_email(item):
    if item["source"] == "Realtor.com":
        return parse_realtor_email(
            item["body"]
        )

    if item["source"] == "Zillow":
        return parse_zillow_email(
            item["subject"],
            item["body"]
        )

    return []


def normalize_address(address):
    return re.sub(
        r"[^a-z0-9]",
        "",
        address.lower()
    )


def completeness_score(listing):
    fields = [
        "price",
        "bedrooms",
        "bathrooms",
        "square_feet"
    ]

    return sum(
        listing.get(field) is not None
        for field in fields
    )


def get_unique_listings():
    emails = fetch_listing_emails(limit=50)

    listings = []

    for item in emails:
        listings.extend(
            extract_listings_from_email(item)
        )

    unique = {}

    for listing in listings:
        key = normalize_address(
            listing["address"]
        )

        if key not in unique:
            unique[key] = listing
            continue

        existing = unique[key]

        if completeness_score(listing) > completeness_score(existing):
            unique[key] = listing

    return list(unique.values())


if __name__ == "__main__":
    listings = get_unique_listings()

    print()
    print("EXTRACTED REAL LISTINGS")
    print("=" * 70)

    if not listings:
        print("No listings extracted.")

    for listing in listings:
        print()
        print(f"Source: {listing['source']}")
        print(f"Address: {listing['address']}")
        print(f"Price: ${listing['price']:,}")
        print(f"Beds: {listing['bedrooms']}")
        print(f"Baths: {listing['bathrooms']}")
        print(f"Sq Ft: {listing['square_feet']}")
        print("-" * 70)
