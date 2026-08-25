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
    except Exception as error:
        return f"Unable to save water review: {error}", 500

    if not result:
        return "Property not found.", 404

    if approved:
        title = "✅ Water view confirmed"
        message = (
            "This property can now move forward "
            "to final scoring."
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
