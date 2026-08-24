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
  "backyard_water_view": true | false | null,
  "water_view_type": "pond" | "lake" | "marsh" | "intracoastal" | "river" | "ocean" | "other" | null,
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

- Backyard water view is TRUE only if there is evidence the property itself has water visible from or directly behind the backyard/rear patio/porch/lanai.
- A community lake, nearby pond, neighborhood water feature, or water somewhere nearby does NOT count.
- If this cannot be confirmed, use null, not false.
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
