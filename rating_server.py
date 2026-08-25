from flask import Flask, request
from database import rate_property

app = Flask(__name__)


@app.route("/")
def home():
    return "Retirement Home Finder rating service is running."


@app.route("/rate")
def rate():
    property_id = request.args.get("id", type=int)
    rating = request.args.get("rating", "").lower()

    if property_id is None:
        return "Missing property ID.", 400

    if rating not in {"love", "maybe", "no"}:
        return "Invalid rating.", 400

    try:
        result = rate_property(property_id, rating)
    except Exception as error:
        return f"Unable to save rating: {error}", 500

    if not result:
        return "Property not found.", 404

    labels = {
        "love": "❤️ Love it",
        "maybe": "🤔 Maybe",
        "no": "❌ Not interested"
    }

    return f"""
    <html>
        <head>
            <title>Rating Saved</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>

        <body style="
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 60px 20px;
        ">
            <h1>Rating saved!</h1>

            <h2>{labels[rating]}</h2>

            <p>
                You can close this page and return to the email.
            </p>
        </body>
    </html>
    """


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )


@app.route("/water-review")
def water_review():
    from database import set_water_review

    property_id = request.args.get("id", type=int)
    decision = request.args.get("decision", "").lower()

    if property_id is None:
        return "Missing property ID.", 400

    if decision not in {"confirm", "reject"}:
        return "Invalid water-review decision.", 400

    approved = decision == "confirm"

    try:
        result = set_water_review(
            property_id,
            approved
        )

        if not result:
            return "Property not found.", 404

        final_result = None

        if approved:
            from finalize_property import finalize_property

            final_result = finalize_property(
                property_id
            )

    except Exception as error:
        return f"Unable to save water review: {error}", 500

    if approved:
        title = "✅ Water view confirmed"

        message = (
            f"Final scoring complete: "
            f"{final_result.get('match_score')}% — "
            f"{final_result.get('category')}."
        )
    else:
        title = "❌ Water view rejected"
        message = (
            "This property has been removed "
            "from consideration."
        )

    return f"""
    <html>
        <head>
            <title>Water Review Saved</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>

        <body style="
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 60px 20px;
        ">
            <h1>{title}</h1>
            <p>{message}</p>
            <p>You can close this page.</p>
        </body>
    </html>
    """


@app.route("/admin")
def admin_dashboard():
    import os
    import html
    from flask import Response
    from database import get_all_properties

    admin_password = os.getenv("ADMIN_PASSWORD")

    auth = request.authorization

    if (
        not admin_password
        or not auth
        or auth.username != "admin"
        or auth.password != admin_password
    ):
        return Response(
            "Authentication required.",
            401,
            {
                "WWW-Authenticate":
                'Basic realm="Retirement Home Finder Admin"'
            }
        )

    properties = get_all_properties()

    pending = [
        p for p in properties
        if p.get("category") == "PENDING WATER REVIEW"
    ]

    top_matches = [
        p for p in properties
        if p.get("category") in {
            "TOP MATCH",
            "WORTH CONSIDERING"
        }
    ]

    rejected = [
        p for p in properties
        if p.get("category") == "REJECTED"
    ]

    top_matches.sort(
        key=lambda p: p.get("match_score") or 0,
        reverse=True
    )

    def listing_url(p):
        if p.get("listing_url"):
            return p["listing_url"]

        urls = p.get("source_urls") or []

        return urls[0] if urls else None

    def card(p, show_review=False):
        property_id = p.get("id")
        address = html.escape(
            str(p.get("address") or "Unknown address")
        )

        price = p.get("price")
        score = p.get("match_score")
        rating = p.get("rating")
        category = p.get("category")
        url = listing_url(p)

        details = []

        if price is not None:
            details.append(f"${price:,}")

        if p.get("bedrooms") is not None:
            details.append(
                f"{p['bedrooms']} beds"
            )

        if p.get("bathrooms") is not None:
            details.append(
                f"{p['bathrooms']:g} baths"
            )

        if p.get("square_feet") is not None:
            details.append(
                f"{p['square_feet']:,} sq ft"
            )

        output = f"""
        <div class="card">
            <h3>{address}</h3>
            <p>{" | ".join(details)}</p>
            <p><b>Status:</b> {category}</p>
        """

        if score is not None:
            output += f"<p><b>Score:</b> {score}/100</p>"

        if rating:
            output += (
                f"<p><b>Parent rating:</b> "
                f"{html.escape(str(rating))}</p>"
            )

        if url:
            safe_url = html.escape(url, quote=True)

            output += f"""
            <p>
                <a href="{safe_url}" target="_blank">
                    View Listing
                </a>
            </p>
            """

        if show_review and property_id:
            output += f"""
            <p>
                <a class="confirm"
                   href="/water-review?id={property_id}&decision=confirm">
                    ✅ Confirm Water View
                </a>

                <a class="reject"
                   href="/water-review?id={property_id}&decision=reject">
                    ❌ Reject Water View
                </a>
            </p>
            """

        output += "</div>"

        return output

    body = """
    <html>
    <head>
        <title>Retirement Home Finder Admin</title>
        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: auto;
                padding: 25px;
                background: #f7f7f7;
            }

            .card {
                background: white;
                padding: 18px;
                margin: 15px 0;
                border-radius: 10px;
                border: 1px solid #ddd;
            }

            a {
                color: #174ea6;
            }

            .confirm,
            .reject {
                display: inline-block;
                padding: 9px 12px;
                margin: 4px;
                border: 1px solid #ccc;
                border-radius: 6px;
                text-decoration: none;
            }

            .confirm {
                color: green;
            }

            .reject {
                color: darkred;
            }

            .count {
                color: #666;
            }
        </style>
    </head>

    <body>

        <h1>🏡 Retirement Home Finder</h1>
        <p>Your private search dashboard.</p>
    """

    body += (
        f"<h2>🌊 Pending Water Reviews "
        f"<span class='count'>({len(pending)})</span></h2>"
    )

    if pending:
        for p in pending:
            body += card(p, show_review=True)
    else:
        body += "<p>No homes need water review.</p>"

    body += (
        f"<h2>⭐ Current Matches "
        f"<span class='count'>({len(top_matches)})</span></h2>"
    )

    if top_matches:
        for p in top_matches:
            body += card(p)
    else:
        body += "<p>No current qualifying matches.</p>"

    body += (
        f"<h2>❌ Rejected "
        f"<span class='count'>({len(rejected)})</span></h2>"
    )

    for p in rejected[:25]:
        body += card(p)

    body += """
    </body>
    </html>
    """

    return body
