import math
import requests
from golf_reference import GOLF_COURSES
from geopy.geocoders import Nominatim, ArcGIS


USER_AGENT = "retirement-home-finder/1.0"


def haversine_miles(lat1, lon1, lat2, lon2):
    r = 3958.8

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(dlambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return r * c


def geocode_with_census(address):
    url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "format": "json"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        matches = (
            data.get("result", {})
            .get("addressMatches", [])
        )

        if not matches:
            return None

        coords = matches[0]["coordinates"]

        return {
            "latitude": coords["y"],
            "longitude": coords["x"],
            "geocoder": "US Census"
        }

    except Exception as error:
        print(f"Census geocoder error: {error}")
        return None


def geocode_with_osm(address):
    try:
        geolocator = Nominatim(
            user_agent=USER_AGENT,
            timeout=15
        )

        location = geolocator.geocode(
            address,
            country_codes="us"
        )

        if not location:
            return None

        return {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "geocoder": "OpenStreetMap"
        }

    except Exception as error:
        print(f"OSM geocoder error: {error}")
        return None


def clean_geocode_address(address):
    import re

    cleaned = address

    # Remove builder/model wording that often confuses geocoders.
    cleaned = re.sub(
        r"\\bLot\\s+\\d+\\b",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r"\\b(Unit|Apt|Apartment|Suite)\\s+[A-Za-z0-9-]+\\b",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    # Remove common builder model names appearing between
    # the street address and city.
    cleaned = re.sub(
        r"\\s{2,}",
        " ",
        cleaned
    )

    cleaned = cleaned.replace(" ,", ",")

    return cleaned.strip()


def geocode_with_arcgis(address):
    try:
        geolocator = ArcGIS(
            timeout=15
        )

        location = geolocator.geocode(
            address
        )

        if not location:
            return None

        return {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "geocoder": "ArcGIS"
        }

    except Exception as error:
        print(f"ArcGIS geocoder error: {error}")
        return None


_GEOCODE_CACHE = {}


def geocode_address(address):
    if not address:
        return None

    if address in _GEOCODE_CACHE:
        return _GEOCODE_CACHE[address]

    candidates = [
        address,
        clean_geocode_address(address)
    ]

    # Remove duplicates while preserving order.
    candidates = list(dict.fromkeys(candidates))

    for candidate in candidates:

        result = geocode_with_census(candidate)

        if result:
            _GEOCODE_CACHE[address] = result
            return result

        result = geocode_with_osm(candidate)

        if result:
            _GEOCODE_CACHE[address] = result
            return result

        result = geocode_with_arcgis(candidate)

        if result:
            _GEOCODE_CACHE[address] = result
            return result

    return None


_GOLF_CACHE = {}


def find_nearby_golf_courses(
    latitude,
    longitude,
    radius_meters=12000
):
    # Deterministic local golf lookup.
    # Avoids unreliable public Overpass servers.

    radius_miles = radius_meters / 1609.344

    courses = []

    for course in GOLF_COURSES:
        distance = haversine_miles(
            latitude,
            longitude,
            course["latitude"],
            course["longitude"]
        )

        if distance <= radius_miles:
            courses.append({
                "name": course["name"],
                "distance_miles": round(distance, 2)
            })

    courses.sort(
        key=lambda item: item["distance_miles"]
    )

    return courses


BEACH_POINTS = [
    {
        "name": "Garden City Beach",
        "latitude": 33.5807,
        "longitude": -79.0017
    },
    {
        "name": "Surfside Beach",
        "latitude": 33.6060,
        "longitude": -78.9731
    },
    {
        "name": "Myrtle Beach",
        "latitude": 33.6891,
        "longitude": -78.8867
    },
    {
        "name": "North Myrtle Beach",
        "latitude": 33.8160,
        "longitude": -78.6800
    }
]


def get_beach_enrichment(address):
    location = geocode_address(address)

    if not location:
        return {
            "nearest_beach": None,
            "beach_distance_miles": None,
            "beach_nearby": None
        }

    distances = []

    for beach in BEACH_POINTS:
        distance = haversine_miles(
            location["latitude"],
            location["longitude"],
            beach["latitude"],
            beach["longitude"]
        )

        distances.append({
            "name": beach["name"],
            "distance_miles": round(distance, 2)
        })

    distances.sort(
        key=lambda item: item["distance_miles"]
    )

    nearest = distances[0]

    return {
        "nearest_beach": nearest["name"],
        "beach_distance_miles": nearest["distance_miles"],
        "beach_nearby": nearest["distance_miles"] <= 15
    }


def get_golf_enrichment(address):

    location = geocode_address(address)

    if not location:
        return {
            "latitude": None,
            "longitude": None,
            "geocoder": None,
            "nearest_golf_course": None,
            "golf_distance_miles": None,
            "golf_nearby": None
        }

    courses = find_nearby_golf_courses(
        location["latitude"],
        location["longitude"]
    )

    if not courses:
        return {
            **location,
            "nearest_golf_course": None,
            "golf_distance_miles": None,
            "golf_nearby": None
        }

    nearest = courses[0]

    return {
        **location,
        "nearest_golf_course": nearest["name"],
        "golf_distance_miles": nearest["distance_miles"],
        "golf_nearby": nearest["distance_miles"] <= 5
    }


if __name__ == "__main__":

    address = "4040 Longleaf Ln, Murrells Inlet, SC 29576"

    print()
    print("GOLF LOCATION TEST")
    print("-" * 40)

    result = get_golf_enrichment(address)

    for key, value in result.items():
        print(f"{key}: {value}")
