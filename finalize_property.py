from datetime import datetime

from database import (
    get_property_by_id,
    update_property_record
)
from location_enrichment import (
    get_golf_enrichment,
    get_beach_enrichment
)
from beach_drive_time import get_beach_drive_enrichment
from final_scoring import calculate_final_score


def finalize_property(property_id):
    property_data = get_property_by_id(property_id)

    if not property_data:
        raise ValueError("Property not found")

    if property_data.get("water_visual_verified") is not True:
        raise ValueError(
            "Water view must be visually confirmed before final scoring"
        )

    address = property_data.get("address")

    if not address:
        raise ValueError("Property is missing an address")

    print(f"Finalizing: {address}")

    golf = get_golf_enrichment(address)
    beach = get_beach_enrichment(address)
    beach_drive = get_beach_drive_enrichment(address)

    final_data = {
        **property_data,
        **golf,
        **beach,
        **beach_drive,

        "property_type": "single_family",

        "multi_story": (
            False
            if property_data.get("single_story") is True
            else property_data.get("multi_story")
        ),

        "golf_mentioned": (
            True
            if golf.get("nearest_golf_course")
            else property_data.get("golf_mentioned", False)
        ),

        "backyard_water_view": True,
        "water_visual_verified": True,
        "flood_risk": property_data.get(
            "flood_risk",
            "unknown"
        )
    }

    score, category, reasons = calculate_final_score(
        final_data
    )

    final_data.update({
        "match_score": score,
        "category": category,
        "rejected": category == "REJECTED",
        "rejection_reason": (
            reasons[0]
            if category == "REJECTED" and reasons
            else None
        ),
        "reasons": reasons,

        # Treat approval as a new analysis event so it
        # appears in the next daily digest.
        "date_analyzed": datetime.now().isoformat()
    })

    update_property_record(
        property_id,
        final_data
    )

    return final_data


if __name__ == "__main__":
    print("Finalization module ready.")
