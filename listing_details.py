import json
import re
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/149.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}


def clean_text(value):
    if not value:
        return None

    return re.sub(r"\s+", " ", value).strip()


def extract_json_ld(soup):
    items = []

    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):
        try:
            data = json.loads(script.string or "")
            items.append(data)
        except Exception:
            continue

    return items


def find_description_in_json(data):
    if isinstance(data, dict):

        description = data.get("description")

        if isinstance(description, str) and len(description) > 80:
            return clean_text(description)

        for value in data.values():
            result = find_description_in_json(value)

            if result:
                return result

    elif isinstance(data, list):

        for item in data:
            result = find_description_in_json(item)

            if result:
                return result

    return None


def fetch_listing_details(url):
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=25
        )

        print(f"HTTP status: {response.status_code}")

        response.raise_for_status()

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
            "description": None
        }

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    description = None

    # Try JSON-LD first
    json_items = extract_json_ld(soup)

    for item in json_items:
        description = find_description_in_json(item)

        if description:
            break

    # Try social/meta description
    if not description:
        meta = soup.find(
            "meta",
            attrs={"property": "og:description"}
        )

        if meta:
            description = clean_text(
                meta.get("content")
            )

    if not description:
        meta = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        if meta:
            description = clean_text(
                meta.get("content")
            )

    return {
        "success": True,
        "url": url,
        "description": description,
        "page_title": clean_text(
            soup.title.string
            if soup.title
            else None
        )
    }


if __name__ == "__main__":

    listings = [
        {
            "address": "227 Pin Oak Dr, Murrells Inlet, SC 29576",
            "url": (
                "https://www.realtor.com/"
                "realestateandhomes-detail/"
                "227-Pin-Oak-Dr_Murrells-Inlet_SC_29576_M92428-31571"
            )
        },
        {
            "address": "457 Waties Dr, Murrells Inlet, SC 29576",
            "url": (
                "https://www.realtor.com/"
                "realestateandhomes-detail/"
                "457-Waties-Dr_Murrells-Inlet_SC_29576_M91137-62301"
            )
        }
    ]

    for listing in listings:

        print()
        print("=" * 70)
        print(listing["address"])
        print("=" * 70)

        result = fetch_listing_details(
            listing["url"]
        )

        print(
            f"Success: "
            f"{result.get('success')}"
        )

        print(
            f"Title: "
            f"{result.get('page_title')}"
        )

        print()
        print("DESCRIPTION:")
        print(
            result.get("description")
            or "No description extracted."
        )
