# Retirement Home Finder search territory.
#
# Important:
# Some communities outside Myrtle Beach city limits use
# "Myrtle Beach, SC" as their postal address.
# Therefore we do NOT reject a property solely because
# the mailing address contains "Myrtle Beach".
#
# We control Myrtle Beach proper primarily through the
# saved-search geography and later can add a true
# city-boundary/geospatial check.

ALLOWED_AREAS = [
    "Murrells Inlet",
    "Garden City",
    "Garden City Beach",
    "Surfside Beach",
    "Pawleys Island",
    "Litchfield Beach",
    "Little River",
    "North Myrtle Beach",
    "Longs",
    "Socastee",
    "Burgess",
    "Prince Creek",
    "Carolina Forest",
    "Georgetown",
]


def location_allowed(address):
    if not address:
        return False

    text = address.lower()

    # Explicit named areas.
    if any(
        area.lower() in text
        for area in ALLOWED_AREAS
    ):
        return True

    # Myrtle Beach postal addresses are temporarily allowed
    # because Socastee / Carolina Forest / nearby communities
    # can use Myrtle Beach as their mailing city.
    #
    # Actual Myrtle Beach city-limit exclusion will be handled
    # later with geographic coordinates rather than text.
    if "myrtle beach" in text:
        return True

    return False


if __name__ == "__main__":
    tests = [
        "123 Main St, Murrells Inlet, SC 29576",
        "456 Example Rd, Socastee, SC 29588",
        "789 Example Dr, Longs, SC 29568",
        "101 Example Ln, North Myrtle Beach, SC 29582",
        "202 Example Ct, Myrtle Beach, SC 29579",
        "303 Example Way, Pawleys Island, SC 29585",
    ]

    for address in tests:
        print(address, "->", location_allowed(address))
