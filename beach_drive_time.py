import requests

from location_enrichment import (
    geocode_address,
    BEACH_POINTS
)


OSRM_URL = "https://router.project-osrm.org/route/v1/driving"


def get_drive_minutes(
    start_lat,
    start_lon,
    end_lat,
    end_lon
):
    url = (
        f"{OSRM_URL}/"
        f"{start_lon},{start_lat};"
        f"{end_lon},{end_lat}"
    )

    params = {
        "overview": "false",
        "steps": "false"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        routes = data.get("routes", [])

        if not routes:
            return None

        seconds = routes[0].get("duration")

        if seconds is None:
            return None

        return round(seconds / 60, 1)

    except Exception as error:
        print(f"Routing error: {error}")
        return None


def get_beach_drive_enrichment(address):
    location = geocode_address(address)

    if not location:
        return {
            "nearest_beach_by_drive": None,
            "beach_drive_minutes": None,
            "within_20_min_beach": None
        }

    results = []

    for beach in BEACH_POINTS:
        minutes = get_drive_minutes(
            location["latitude"],
            location["longitude"],
            beach["latitude"],
            beach["longitude"]
        )

        if minutes is None:
            continue

        results.append({
            "name": beach["name"],
            "drive_minutes": minutes
        })

    if not results:
        return {
            "nearest_beach_by_drive": None,
            "beach_drive_minutes": None,
            "within_20_min_beach": None
        }

    results.sort(
        key=lambda item: item["drive_minutes"]
    )

    nearest = results[0]

    return {
        "nearest_beach_by_drive": nearest["name"],
        "beach_drive_minutes": nearest["drive_minutes"],
        "within_20_min_beach": nearest["drive_minutes"] <= 20
    }


if __name__ == "__main__":
    tests = [
        "227 Pin Oak Dr, Murrells Inlet, SC 29576",
        "249 Star Lake Dr, Murrells Inlet, SC 29576"
    ]

    for address in tests:
        print()
        print(address)
        print("-" * 60)

        result = get_beach_drive_enrichment(address)

        for key, value in result.items():
            print(f"{key}: {value}")
