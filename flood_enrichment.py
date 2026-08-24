import requests


FEMA_URL = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/28/query"


def get_flood_zone(latitude, longitude):
    if latitude is None or longitude is None:
        return {
            "flood_zone": None,
            "flood_risk": "unknown"
        }

    params = {
        "geometry": f"{longitude},{latitude}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "false",
        "f": "json"
    }

    try:
        response = requests.get(
            FEMA_URL,
            params=params,
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        features = data.get("features", [])

        if not features:
            return {
                "flood_zone": None,
                "flood_risk": "unknown"
            }

        attributes = features[0].get("attributes", {})

        zone = (
            attributes.get("FLD_ZONE")
            or attributes.get("ZONE_SUBTY")
            or attributes.get("SFHA_TF")
        )

        if not zone:
            return {
                "flood_zone": None,
                "flood_risk": "unknown"
            }

        zone_text = str(zone).upper()

        high_risk_zones = (
            "A",
            "AE",
            "AH",
            "AO",
            "V",
            "VE"
        )

        moderate_zones = (
            "X500",
            "0.2 PCT"
        )

        if zone_text.startswith(high_risk_zones):
            risk = "high"

        elif any(value in zone_text for value in moderate_zones):
            risk = "moderate"

        elif zone_text.startswith("X"):
            risk = "low"

        else:
            risk = "unknown"

        return {
            "flood_zone": zone,
            "flood_risk": risk
        }

    except Exception as error:
        print(f"Flood lookup error: {error}")

        return {
            "flood_zone": None,
            "flood_risk": "unknown"
        }


if __name__ == "__main__":

    latitude = 33.55490522203
    longitude = -79.058567843201

    print()
    print("FLOOD RISK TEST")
    print("-" * 40)

    result = get_flood_zone(
        latitude,
        longitude
    )

    for key, value in result.items():
        print(f"{key}: {value}")
