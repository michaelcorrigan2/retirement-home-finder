import base64
import json
import re
from urllib.parse import urlparse, parse_qs

from email_intake import fetch_listing_emails


def decode_base64url(value):
    value += "=" * (-len(value) % 4)

    return base64.urlsafe_b64decode(
        value
    ).decode(
        "utf-8",
        errors="ignore"
    )


def extract_realtor_url(url):
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        jwt_payload = params.get("jwtP")

        if not jwt_payload:
            return None

        decoded = decode_base64url(
            jwt_payload[0]
        )

        data = json.loads(decoded)

        return data.get("linkUrl")

    except Exception:
        return None


def extract_zillow_url(url):
    match = re.search(
        r"/zpid_target/(\d+)_zpid/",
        url
    )

    if not match:
        return None

    zpid = match.group(1)

    return (
        f"https://www.zillow.com/"
        f"homedetails/{zpid}_zpid/"
    )


def get_property_links():
    emails = fetch_listing_emails(limit=50)

    results = []

    for item in emails:

        for link in item.get("links", []):

            url = link.get("url", "")
            label = link.get("label", "")

            property_url = None

            if item["source"] == "Realtor.com":
                property_url = extract_realtor_url(
                    url
                )

            elif item["source"] == "Zillow":
                property_url = extract_zillow_url(
                    url
                )

            if not property_url:
                continue

            results.append({
                "source": item["source"],
                "label": label,
                "url": property_url
            })

    unique = {}

    for result in results:
        unique[result["url"]] = result

    return list(unique.values())


if __name__ == "__main__":

    links = get_property_links()

    print()
    print("REAL PROPERTY LINKS")
    print("=" * 80)

    for item in links:
        print()
        print(f"Source: {item['source']}")
        print(f"Label: {item['label']}")
        print(f"URL: {item['url']}")
        print("-" * 80)
