import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(dotenv_path=".env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def research_property(address):
    prompt = f"""
Research this residential property using current public web information:

{address}

Return ONLY valid JSON with this exact structure:

{{
  "address": "{address}",
  "price": integer | null,
  "bedrooms": integer | null,
  "bathrooms": number | null,
  "square_feet": integer | null,
  "year_built": integer | null,
  "backyard_water_view": true | false | null,
  "water_view_type": "pond" | "lake" | "marsh" | "intracoastal" | "river" | "ocean" | "other" | null,
  "water_view_evidence_type": "explicit_rear_view_text" | "generic_water_text" | "none" | null,
  "single_story": true | false | null,
  "move_in_ready": true | false | null,
  "community_55_plus": true | false | null,
  "garage_spaces": integer | null,
  "fully_furnished": true | false | null,
  "amenities": [],
  "renovated": true | false | null,
  "evidence_summary": "",
  "source_urls": []
}}

Important rules:

- Verify price, bedrooms, bathrooms, square footage, and year built from current property-specific listing sources when available.
- Prefer current MLS/brokerage/listing data over old sale records.
- For price, return the current asking price, not a previous sale price.
- For square_feet, return the listed living area, not lot size.
- If sources conflict materially, prefer the most recent current listing and mention the conflict in evidence_summary.

- Backyard water view is TRUE only when property-specific listing text explicitly states that water is visible from the backyard, rear yard, rear patio, rear porch, screened porch, or lanai.
- If listing text only says waterfront, pond on lot, lakefront, water nearby, community pond, or similar without saying it is visible from the rear living area, use null.
- Set water_view_evidence_type to "explicit_rear_view_text" only when the listing explicitly connects the water view to the backyard/rear porch/patio/lanai.
- Set it to "generic_water_text" when water is mentioned but the actual rear view is not clearly established.
- Set it to "none" when there is no relevant water evidence.
- IMPORTANT: even explicit_rear_view_text is only textual evidence. It does NOT mean the view has been visually verified from listing photos.
- If uncertain, use null rather than true.
- For single_story, distinguish true one-level living from homes that clearly have bedrooms/living areas upstairs.
- If a field cannot be verified, use null.
- Do not guess.
- Prefer current listing pages, brokerage listings, MLS syndication pages, builder pages, and other reputable real-estate sources.
"""

    response = client.responses.create(
        model="gpt-5-mini",
        tools=[
            {
                "type": "web_search"
            }
        ],
        input=prompt
    )

    text = response.output_text.strip()

    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()

    return json.loads(text)


if __name__ == "__main__":

    addresses = [
        "227 Pin Oak Dr, Murrells Inlet, SC 29576",
        "457 Waties Dr, Murrells Inlet, SC 29576"
    ]

    for address in addresses:
        print()
        print("=" * 70)
        print(address)
        print("=" * 70)

        try:
            result = research_property(address)

            print(
                json.dumps(
                    result,
                    indent=2
                )
            )

        except Exception as error:
            print(
                f"Research error: {error}"
            )
