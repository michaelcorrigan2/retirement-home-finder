import re
from urllib.parse import urlparse, parse_qs, unquote

from email_intake import fetch_listing_emails


def unwrap_recursive(url, max_rounds=5):
    current = url

    for _ in range(max_rounds):
        try:
            decoded = unquote(current)
            parsed = urlparse(decoded)
            params = parse_qs(parsed.query)

            target = None

            for key in [
                "target",
                "url",
                "redirect",
                "redirect_url",
                "destination",
                "dest"
            ]:
                if key in params and params[key]:
                    target = params[key][0]
                    break

            if not target:
                return decoded

            if target == current:
                return decoded

            current = target

        except Exception:
            return current

    return current


def urls_from_text(text):
    return re.findall(
        r'https?://[^\s<>"\']+',
        text or ""
    )


emails = fetch_listing_emails(limit=50)

print()
print("DECODED LISTING LINK DEBUG")
print("=" * 80)

for item in emails:

    print()
    print(f"SOURCE: {item['source']}")
    print(f"SUBJECT: {item['subject']}")
    print("-" * 80)

    candidates = []

    for link in item.get("links", []):
        candidates.append(
            (
                link.get("label", ""),
                link.get("url", "")
            )
        )

    for url in urls_from_text(item.get("body", "")):
        candidates.append(
            ("BODY URL", url)
        )

    seen = set()

    for label, url in candidates:
        final_url = unwrap_recursive(url)

        key = (label, final_url)

        if key in seen:
            continue

        seen.add(key)

        interesting_text = (
            label + " " + final_url
        ).lower()

        if any(term in interesting_text for term in [
            "227 pin oak",
            "457 waties",
            "view listing",
            "homedetail",
            "realestateandhomes",
            "property",
            "listing"
        ]):
            print()
            print(f"LABEL: {label[:120]}")
            print(f"URL:   {final_url[:1000]}")

    print()
    print("=" * 80)
