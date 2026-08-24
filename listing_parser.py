import re


def clean_text(text):
    return " ".join(text.split())


def extract_price(text):
    match = re.search(r"\$([\d,]+)", text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def extract_bedrooms(text):
    patterns = [
        r"(\d+)\s*(?:bd|bed|beds|bedroom|bedrooms)",
        r"(\d+)\s*BR\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))

    return None


def extract_bathrooms(text):
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:ba|bath|baths|bathroom|bathrooms)",
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    return float(match.group(1))


def extract_square_feet(text):
    match = re.search(
        r"([\d,]+)\s*(?:sq\.?\s*ft\.?|sqft|square feet)",
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    return int(match.group(1).replace(",", ""))


def extract_address(text):
    pattern = (
        r"\b\d{1,6}\s+"
        r"[A-Za-z0-9.'\- ]+\s+"
        r"(?:Street|St|Road|Rd|Drive|Dr|Lane|Ln|Court|Ct|"
        r"Circle|Cir|Boulevard|Blvd|Way|Avenue|Ave|Place|Pl|"
        r"Trail|Trl|Parkway|Pkwy)"
        r"(?:\s+[A-Za-z0-9.'\- ]+)?"
        r",?\s+"
        r"(?:Murrells Inlet|North Myrtle Beach|Surfside Beach|"
        r"Garden City|Pawleys Island|Little River)"
        r",?\s+SC"
        r"(?:\s+\d{5})?"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return clean_text(match.group(0))

    return None


def extract_listing_url(text):
    match = re.search(r"https?://[^\s<>]+", text)

    if not match:
        return None

    return match.group(0).rstrip(").,]")


def detect_fully_furnished(text):
    phrases = [
        "fully furnished",
        "sold furnished",
        "comes furnished",
        "furnishings included",
        "furniture included"
    ]

    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def detect_generic_water_view(text):
    phrases = [
        "water view",
        "water views",
        "pond view",
        "pond views",
        "lake view",
        "lake views",
        "marsh view",
        "marsh views",
        "intracoastal view",
        "intracoastal views",
        "river view",
        "river views",
        "ocean view",
        "ocean views",
        "lagoon view",
        "lagoon views"
    ]

    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def detect_backyard_water_view(text):
    lowered = text.lower()

    strong_phrases = [
        "backyard pond view",
        "backyard lake view",
        "backyard water view",
        "backyard marsh view",
        "backyard lagoon view",
        "pond in the backyard",
        "lake in the backyard",
        "water in the backyard",
        "marsh in the backyard",
        "lagoon in the backyard",
        "backs to a pond",
        "backs up to a pond",
        "backs to the lake",
        "backs up to the lake",
        "backs to water",
        "backs up to water",
        "backs to the marsh",
        "backs up to the marsh",
        "overlooking the pond from the backyard",
        "overlooking the lake from the backyard",
        "overlooking the water from the backyard",
        "water view from the backyard",
        "pond view from the backyard",
        "lake view from the backyard",
        "marsh view from the backyard",
        "water views from the rear",
        "pond views from the rear",
        "lake views from the rear",
        "rear water view",
        "rear pond view",
        "rear lake view",
        "rear marsh view",
        "waterfront backyard",
        "pond-front backyard",
        "lakefront backyard"
    ]

    if any(phrase in lowered for phrase in strong_phrases):
        return True

    # Flexible proximity check:
    # look for backyard/rear/patio/lanai near a water term.
    water_terms = [
        "pond",
        "lake",
        "water",
        "marsh",
        "lagoon",
        "intracoastal",
        "river"
    ]

    rear_terms = [
        "backyard",
        "back yard",
        "rear yard",
        "rear",
        "patio",
        "screened porch",
        "screened-in porch",
        "lanai"
    ]

    sentences = re.split(r"[.!?]", lowered)

    for sentence in sentences:
        has_water = any(term in sentence for term in water_terms)
        has_rear = any(term in sentence for term in rear_terms)

        if has_water and has_rear:
            return True

    return False


def detect_multi_story(text):
    phrases = [
        "upstairs",
        "second floor",
        "2nd floor",
        "two story",
        "two-story",
        "additional bedrooms upstairs",
        "bedrooms upstairs"
    ]

    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def detect_single_story(text):
    phrases = [
        "single story",
        "single-story",
        "one story",
        "one-story",
        "ranch style",
        "ranch-style",
        "all on one level",
        "one level living"
    ]

    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def detect_move_in_ready(text):
    positive_phrases = [
        "move-in ready",
        "move in ready",
        "turnkey",
        "turn-key",
        "recently renovated",
        "recently remodeled",
        "fully renovated",
        "updated throughout"
    ]

    negative_phrases = [
        "fixer upper",
        "fixer-upper",
        "needs work",
        "needs renovation",
        "investor special",
        "handyman special"
    ]

    lowered = text.lower()

    if any(phrase in lowered for phrase in negative_phrases):
        return False

    if any(phrase in lowered for phrase in positive_phrases):
        return True

    return None


def parse_listing_text(text):
    text = clean_text(text)

    single_story = detect_single_story(text)
    multi_story = detect_multi_story(text)

    if multi_story:
        single_story = False

    generic_water_view = detect_generic_water_view(text)
    backyard_water_view = detect_backyard_water_view(text)

    return {
        "address": extract_address(text),
        "price": extract_price(text),
        "bedrooms": extract_bedrooms(text),
        "bathrooms": extract_bathrooms(text),
        "square_feet": extract_square_feet(text),
        "listing_url": extract_listing_url(text),
        "fully_furnished": detect_fully_furnished(text),

        # Generic mention of any water view.
        "water_view": generic_water_view,

        # This is the IMPORTANT field for your parents.
        "backyard_water_view": backyard_water_view,

        "single_story": single_story,
        "multi_story": multi_story,
        "move_in_ready": detect_move_in_ready(text)
    }


if __name__ == "__main__":
    sample_text = """
    456 Coastal View Dr, Murrells Inlet, SC 29576

    $539,900
    3 beds
    2 baths
    2,180 sq ft

    Beautiful single-story move-in ready home.
    Enjoy peaceful pond views directly from the backyard
    and screened porch.

    Two-car garage.

    https://www.example.com/listing/456
    """

    listing = parse_listing_text(sample_text)

    print()
    print("BACKYARD WATER TEST")
    print("-" * 40)

    for key, value in listing.items():
        print(f"{key}: {value}")
