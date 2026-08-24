import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

from dotenv import load_dotenv
from daily_digest import build_digest
from database import get_all_properties


load_dotenv(".env")

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

RECIPIENTS = [
    os.getenv("PARENT_EMAIL_1"),
    os.getenv("PARENT_EMAIL_2"),
    os.getenv("YOUR_EMAIL")
]

RECIPIENTS = [
    email_address
    for email_address in RECIPIENTS
    if email_address
]

RATING_BASE_URL = (
    "https://retirement-home-ratings.onrender.com/rate"
)


def is_today(date_string):
    if not date_string:
        return False

    try:
        analyzed = datetime.fromisoformat(
            date_string.replace("Z", "+00:00")
        )
        return analyzed.date() == datetime.now().date()

    except ValueError:
        return False


def yes_no_unknown(value):
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return "Not confirmed"


def build_html_digest():
    properties = get_all_properties()

    todays_properties = [
        item
        for item in properties
        if is_today(item.get("date_analyzed"))
        and item.get("category") in {
            "TOP MATCH",
            "WORTH CONSIDERING"
        }
        and item.get("backyard_water_view") is True
    ]

    todays_properties.sort(
        key=lambda item: item.get("match_score", 0),
        reverse=True
    )

    today = datetime.now().strftime("%B %d, %Y")

    html = f"""
    <html>
    <body style="
        font-family: Arial, sans-serif;
        max-width: 700px;
        margin: auto;
        padding: 24px;
        color: #222;
    ">
        <h1 style="margin-bottom: 4px;">
            Retirement Home Daily Digest
        </h1>

        <p style="color:#666;">
            {today}
        </p>
    """

    if not todays_properties:
        html += """
        <p>
            No new homes met all mandatory requirements
            and the 75% match threshold today.
        </p>
        </body>
        </html>
        """

        return html

    for property_data in todays_properties:
        property_id = property_data.get("id")
        address = property_data.get(
            "address",
            "Unknown address"
        )
        score = property_data.get("match_score")
        category = property_data.get("category")
        price = property_data.get("price")
        beds = property_data.get("bedrooms")
        baths = property_data.get("bathrooms")
        sqft = property_data.get("square_feet")

        water_type = property_data.get(
            "water_view_type"
        )

        golf = property_data.get(
            "nearest_golf_course"
        )
        golf_distance = property_data.get(
            "golf_distance_miles"
        )

        beach = property_data.get(
            "nearest_beach"
        )
        beach_distance = property_data.get(
            "beach_distance_miles"
        )

        garage = property_data.get(
            "garage_spaces"
        )

        listing_url = property_data.get(
            "listing_url"
        )

        if not listing_url:
            sources = (
                property_data.get("source_urls")
                or []
            )

            if sources:
                listing_url = sources[0]

        details = []

        if price is not None:
            details.append(f"${price:,}")

        if beds is not None:
            details.append(f"{beds} beds")

        if baths is not None:
            details.append(f"{baths:g} baths")

        if sqft is not None:
            details.append(f"{sqft:,} sq ft")

        detail_text = " | ".join(details)

        html += f"""
        <div style="
            border:1px solid #ddd;
            border-radius:12px;
            padding:20px;
            margin:24px 0;
        ">

            <h2 style="margin-top:0;">
                🏡 {address}
            </h2>

            <p style="
                font-size:18px;
                font-weight:bold;
            ">
                {score}/100 — {category}
            </p>

            <p>{detail_text}</p>

            <hr style="border:none;border-top:1px solid #eee;">

            <p>
                🌊 <b>Backyard water:</b>
                {yes_no_unknown(
                    property_data.get(
                        "backyard_water_view"
                    )
                )}
                {
                    f" ({water_type.title()})"
                    if water_type
                    else ""
                }
            </p>

            <p>
                🏡 <b>Single-story:</b>
                {yes_no_unknown(
                    property_data.get(
                        "single_story"
                    )
                )}
            </p>

            <p>
                🚗 <b>Garage:</b>
                {
                    f"{garage}-car"
                    if garage is not None
                    else "Not confirmed"
                }
            </p>

            <p>
                ⛳ <b>Golf:</b>
                {
                    f"{golf} ({golf_distance} miles)"
                    if golf and golf_distance is not None
                    else (
                        golf
                        if golf
                        else "Not confirmed"
                    )
                }
            </p>

            <p>
                🏖️ <b>Beach:</b>
                {
                    f"{beach} ({beach_distance} miles)"
                    if beach and beach_distance is not None
                    else (
                        beach
                        if beach
                        else "Not confirmed"
                    )
                }
            </p>

            <p>
                🏘️ <b>55+ community:</b>
                {yes_no_unknown(
                    property_data.get(
                        "community_55_plus"
                    )
                )}
            </p>

            <p>
                🛋️ <b>Fully furnished:</b>
                {yes_no_unknown(
                    property_data.get(
                        "fully_furnished"
                    )
                )}
            </p>
        """

        if listing_url:
            html += f"""
            <p style="margin-top:22px;">
                <a href="{listing_url}"
                   style="
                       display:inline-block;
                       padding:11px 18px;
                       background:#222;
                       color:white;
                       text-decoration:none;
                       border-radius:6px;
                   ">
                    View Listing
                </a>
            </p>
            """

        if property_id is not None:
            love_url = (
                f"{RATING_BASE_URL}"
                f"?id={property_id}&rating=love"
            )

            maybe_url = (
                f"{RATING_BASE_URL}"
                f"?id={property_id}&rating=maybe"
            )

            no_url = (
                f"{RATING_BASE_URL}"
                f"?id={property_id}&rating=no"
            )

            html += f"""
            <p style="
                margin-top:24px;
                font-weight:bold;
            ">
                What do you think?
            </p>

            <p>
                <a href="{love_url}"
                   style="
                       display:inline-block;
                       padding:10px 15px;
                       margin-right:8px;
                       border:1px solid #ccc;
                       border-radius:6px;
                       text-decoration:none;
                   ">
                    ❤️ Love
                </a>

                <a href="{maybe_url}"
                   style="
                       display:inline-block;
                       padding:10px 15px;
                       margin-right:8px;
                       border:1px solid #ccc;
                       border-radius:6px;
                       text-decoration:none;
                   ">
                    🤔 Maybe
                </a>

                <a href="{no_url}"
                   style="
                       display:inline-block;
                       padding:10px 15px;
                       border:1px solid #ccc;
                       border-radius:6px;
                       text-decoration:none;
                   ">
                    ❌ No
                </a>
            </p>
            """

        html += """
        </div>
        """

    html += """
    </body>
    </html>
    """

    return html


def send_daily_digest():
    text_digest = build_digest()
    html_digest = build_html_digest()

    today = datetime.now().strftime(
        "%B %d, %Y"
    )

    message = EmailMessage()

    message["From"] = GMAIL_ADDRESS
    message["To"] = ", ".join(RECIPIENTS)
    message["Subject"] = (
        f"Retirement Home Matches — {today}"
    )

    # Plain-text fallback
    message.set_content(text_digest)

    # Rich HTML version
    message.add_alternative(
        html_digest,
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

    print()
    print("✅ DAILY DIGEST SENT")

    for recipient in RECIPIENTS:
        print(f"- {recipient}")


if __name__ == "__main__":
    send_daily_digest()
