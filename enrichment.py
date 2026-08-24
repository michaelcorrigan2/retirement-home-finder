def contains_any(text, phrases):
    text = text.lower()
    return any(phrase.lower() in text for phrase in phrases)


def detect_garage_spaces(text):
    text_lower = text.lower()

    if contains_any(text_lower, [
        "3-car garage",
        "3 car garage",
        "three-car garage",
        "three car garage"
    ]):
        return 3

    if contains_any(text_lower, [
        "2-car garage",
        "2 car garage",
        "two-car garage",
        "two car garage"
    ]):
        return 2

    if contains_any(text_lower, [
        "1-car garage",
        "1 car garage",
        "one-car garage",
        "one car garage"
    ]):
        return 1

    return None


def detect_55_plus(text):
    return contains_any(text, [
        "55+",
        "55 plus",
        "55 and older",
        "active adult",
        "age-restricted community",
        "age restricted community",
        "adult community"
    ])


def detect_golf(text):
    return contains_any(text, [
        "golf course",
        "golf community",
        "golf club",
        "golfing",
        "golf"
    ])


def detect_amenities(text):
    amenities = []

    checks = {
        "pool": [
            "community pool",
            "swimming pool",
            "outdoor pool",
            "indoor pool",
            "pool"
        ],
        "clubhouse": [
            "clubhouse",
            "club house"
        ],
        "tennis": [
            "tennis court",
            "tennis courts",
            "tennis"
        ],
        "pickleball": [
            "pickleball court",
            "pickleball courts",
            "pickleball"
        ],
        "fitness_center": [
            "fitness center",
            "fitness centre",
            "gym"
        ]
    }

    for amenity, phrases in checks.items():
        if contains_any(text, phrases):
            amenities.append(amenity)

    return amenities


def detect_renovated(text):
    return contains_any(text, [
        "recently renovated",
        "fully renovated",
        "recently remodeled",
        "recently updated",
        "updated throughout",
        "newly renovated",
        "newly remodeled"
    ])


def enrich_from_listing_text(text):
    return {
        "garage_spaces": detect_garage_spaces(text),
        "community_55_plus": detect_55_plus(text),
        "golf_mentioned": detect_golf(text),
        "amenities": detect_amenities(text),
        "renovated": detect_renovated(text),

        # These require outside geographic/risk data later.
        "golf_minutes": None,
        "beach_minutes": None,
        "flood_risk": "unknown"
    }


if __name__ == "__main__":
    sample = """
    Beautiful move-in ready home in an active adult 55+ golf community.
    Features a two-car garage, community pool, clubhouse,
    pickleball courts and tennis courts.
    Recently renovated kitchen and bathrooms.
    """

    result = enrich_from_listing_text(sample)

    print()
    print("ENRICHMENT TEST")
    print("-" * 40)

    for key, value in result.items():
        print(f"{key}: {value}")
