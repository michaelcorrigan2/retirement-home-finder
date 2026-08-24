import os
from datetime import datetime

from dotenv import load_dotenv
from supabase import create_client


load_dotenv(".env")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


def normalize_address(address):
    return "".join(
        character.lower()
        for character in (address or "")
        if character.isalnum()
    )


def property_exists(address):
    result = (
        supabase
        .table("properties")
        .select("id,address")
        .eq("address", address)
        .limit(1)
        .execute()
    )

    return len(result.data) > 0


def save_property(record):
    address = record.get("address")

    if not address:
        raise ValueError("Property record is missing address")

    if property_exists(address):
        return False

    row = {
        "address": address,
        "listing_url": record.get("listing_url"),
        "match_score": record.get("match_score"),
        "category": record.get("category"),
        "data": record,
        "date_analyzed": record.get(
            "date_analyzed",
            datetime.now().isoformat()
        )
    }

    supabase.table("properties").insert(row).execute()

    return True


def get_all_properties():
    result = (
        supabase
        .table("properties")
        .select("*")
        .execute()
    )

    properties = []

    for row in result.data:
        data = row.get("data") or {}

        if not data.get("address"):
            data["address"] = row.get("address")

        if data.get("match_score") is None:
            data["match_score"] = row.get("match_score")

        if not data.get("category"):
            data["category"] = row.get("category")

        if not data.get("date_analyzed"):
            data["date_analyzed"] = row.get("date_analyzed")

        # Include database fields needed by the email/rating system.
        data["id"] = row.get("id")
        data["rating"] = row.get("rating")

        if not data.get("listing_url"):
            data["listing_url"] = row.get("listing_url")

        properties.append(data)

    return properties


if __name__ == "__main__":
    print("Database module ready.")
    print("Current properties:", len(get_all_properties()))


def rate_property(property_id, rating):
    allowed = {"love", "maybe", "no"}

    if rating not in allowed:
        raise ValueError("Invalid rating")

    result = (
        supabase
        .table("properties")
        .update({"rating": rating})
        .eq("id", property_id)
        .execute()
    )

    return result.data


def rate_property(property_id, rating):
    allowed = {"love", "maybe", "no"}

    if rating not in allowed:
        raise ValueError("Invalid rating")

    result = (
        supabase
        .table("properties")
        .update({"rating": rating})
        .eq("id", property_id)
        .execute()
    )

    return result.data
