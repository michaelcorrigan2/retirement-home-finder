import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from database import get_all_properties


load_dotenv(".env")

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
YOUR_EMAIL = os.getenv("YOUR_EMAIL")

BASE_URL = "https://retirement-home-ratings.onrender.com/water-review"


def get_listing_url(property_data):
    url = property_data.get("listing_url")

    if url:
        return url

    source_urls = property_data.get("source_urls") or []

    if source_urls:
        return source_urls[0]

    return None


def get_pending_water_reviews():
    return [
        item
        for item in get_all_properties()
        if item.get("category") == "PENDING WATER REVIEW"
        and item.get("water_visual_verified") is not True
    ]


def build_html():
    pending = get_pending_water_reviews()

    if not pending:
        return None

    html = """
    <html>
    <body style="
        font-family: Arial, sans-serif;
        max-width: 700px;
        margin: auto;
        padding: 24px;
        color: #222;
    ">

    <h1>Water View Review Needed</h1>

    <p>
        These homes otherwise look promising, but the backyard
        water view needs visual confirmation before they can be scored.
    </p>
    """

    for item in pending:
        property_id = item.get("id")
        address = item.get("address", "Unknown address")
        price = item.get("price")
        beds = item.get("bedrooms")
        baths = item.get("bathrooms")
        sqft = item.get("square_feet")
        listing_url = get_listing_url(item)

        details = []

        if price is not None:
            details.append(f"${price:,}")

        if beds is not None:
            details.append(f"{beds} beds")

        if baths is not None:
            details.append(f"{baths:g} baths")

        if sqft is not None:
            details.append(f"{sqft:,} sq ft")

        confirm_url = (
            f"{BASE_URL}?id={property_id}&decision=confirm"
        )

        reject_url = (
            f"{BASE_URL}?id={property_id}&decision=reject"
        )

        html += f"""
        <div style="
            border:1px solid #ddd;
            border-radius:12px;
            padding:20px;
            margin:24px 0;
        ">

            <h2>🏡 {address}</h2>

            <p>{" | ".join(details)}</p>

            <p>
                Listing text suggests a rear/backyard water view,
                but this must be visually confirmed.
            </p>
        """

        if listing_url:
            html += f"""
            <p>
                <a href="{listing_url}"
                   style="
                       display:inline-block;
                       padding:10px 16px;
                       background:#222;
                       color:#fff;
                       text-decoration:none;
                       border-radius:6px;
                   ">
                    View Listing Photos
                </a>
            </p>
            """

        html += f"""
            <p style="margin-top:20px;">
                <a href="{confirm_url}"
                   style="
                       display:inline-block;
                       padding:10px 16px;
                       margin-right:8px;
                       border:1px solid #aaa;
                       border-radius:6px;
                       text-decoration:none;
                   ">
                    ✅ Confirm Water View
                </a>

                <a href="{reject_url}"
                   style="
                       display:inline-block;
                       padding:10px 16px;
                       border:1px solid #aaa;
                       border-radius:6px;
                       text-decoration:none;
                   ">
                    ❌ Reject Water View
                </a>
            </p>

        </div>
        """

    html += """
    </body>
    </html>
    """

    return html


def send_water_review_email():
    html = build_html()

    if not html:
        print("No pending water reviews.")
        return False

    message = EmailMessage()

    message["From"] = GMAIL_ADDRESS
    message["To"] = YOUR_EMAIL
    message["Subject"] = "🌊 Water View Review Needed"

    message.set_content(
        "One or more retirement-home candidates need visual water-view review."
    )

    message.add_alternative(
        html,
        subtype="html"
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as smtp:

        smtp.login(
            GMAIL_ADDRESS,
            GMAIL_APP_PASSWORD
        )

        smtp.send_message(message)

    print("✅ Water review email sent.")
    return True


if __name__ == "__main__":
    send_water_review_email()
