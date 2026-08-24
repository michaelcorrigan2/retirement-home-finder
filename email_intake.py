import imaplib
import email
import os
import re
from email.header import decode_header
from urllib.parse import urlparse, parse_qs, unquote

from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def decode_text(value):
    if not value:
        return ""

    result = ""

    for part, encoding in decode_header(value):
        if isinstance(part, bytes):
            result += part.decode(
                encoding or "utf-8",
                errors="ignore"
            )
        else:
            result += part

    return result


def clean_text(text):
    return re.sub(r"\s+", " ", text or "").strip()


def unwrap_tracking_url(url):
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        if "target" in params:
            return unquote(params["target"][0])

        return url
    except Exception:
        return url


def extract_html_links(html):
    links = []

    soup = BeautifulSoup(html, "html.parser")

    for anchor in soup.find_all("a", href=True):
        href = unwrap_tracking_url(anchor["href"])
        label = clean_text(anchor.get_text(" ", strip=True))

        links.append({
            "label": label,
            "url": href
        })

    return links


def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["style", "script", "head"]):
        tag.decompose()

    return clean_text(
        soup.get_text(" ", strip=True)
    )


def get_email_content(message):
    plain_parts = []
    html_parts = []
    links = []

    if message.is_multipart():

        for part in message.walk():
            disposition = str(
                part.get("Content-Disposition", "")
            )

            if "attachment" in disposition:
                continue

            content_type = part.get_content_type()
            payload = part.get_payload(decode=True)

            if not payload:
                continue

            charset = part.get_content_charset() or "utf-8"

            decoded = payload.decode(
                charset,
                errors="ignore"
            )

            if content_type == "text/plain":
                plain_parts.append(decoded)

            elif content_type == "text/html":
                html_parts.append(decoded)
                links.extend(
                    extract_html_links(decoded)
                )

    else:
        payload = message.get_payload(decode=True)

        if payload:
            decoded = payload.decode(
                message.get_content_charset() or "utf-8",
                errors="ignore"
            )

            if message.get_content_type() == "text/html":
                html_parts.append(decoded)
                links.extend(
                    extract_html_links(decoded)
                )
            else:
                plain_parts.append(decoded)

    plain_text = clean_text(
        " ".join(plain_parts)
    )

    if plain_text and len(
        re.findall(r"[{};]", plain_text)
    ) < 20:
        body = plain_text

    elif html_parts:
        body = html_to_text(
            " ".join(html_parts)
        )

    else:
        body = plain_text

    return body, links


def determine_source(sender, subject):
    text = f"{sender} {subject}".lower()

    if "redfin" in text:
        return "Redfin"

    if "zillow" in text:
        return "Zillow"

    if "realtor" in text:
        return "Realtor.com"

    return None


def is_listing_alert(source, subject, body):
    text = f"{subject} {body}".lower()

    exclude_phrases = [
        "welcome",
        "verify your email",
        "shared some google account data",
        "housing market news",
        "newsletter",
        "password",
        "security"
    ]

    if any(
        phrase in text
        for phrase in exclude_phrases
    ):
        return False

    signals = [
        "new listing",
        "new listings",
        "saved search",
        "latest results"
    ]

    return any(
        signal in text
        for signal in signals
    )


def fetch_listing_emails(limit=50):
    mail = imaplib.IMAP4_SSL(
        "imap.gmail.com"
    )

    mail.login(
        GMAIL_ADDRESS,
        GMAIL_APP_PASSWORD
    )

    mail.select("inbox")

    status, data = mail.search(
        None,
        "ALL"
    )

    message_ids = data[0].split()

    results = []

    for message_id in reversed(
        message_ids[-limit:]
    ):
        status, msg_data = mail.fetch(
            message_id,
            "(RFC822)"
        )

        if status != "OK":
            continue

        message = email.message_from_bytes(
            msg_data[0][1]
        )

        sender = decode_text(
            message.get("From")
        )

        subject = decode_text(
            message.get("Subject")
        )

        source = determine_source(
            sender,
            subject
        )

        if not source:
            continue

        body, links = get_email_content(
            message
        )

        if not is_listing_alert(
            source,
            subject,
            body
        ):
            continue

        results.append({
            "message_id": message_id.decode(),
            "source": source,
            "subject": subject,
            "body": body,
            "links": links
        })

    mail.logout()

    return results


if __name__ == "__main__":
    emails = fetch_listing_emails()

    print()
    print("LISTING LINKS")
    print("=" * 70)

    for item in emails:
        print()
        print(item["source"])
        print(item["subject"])

        interesting = []

        for link in item["links"]:
            url = link["url"].lower()

            if (
                "realtor.com/realestateandhomes-detail" in url
                or "zillow.com/homedetails" in url
                or "redfin.com/" in url
            ):
                interesting.append(link)

        for link in interesting[:10]:
            print(
                f"{link['label']}: "
                f"{link['url']}"
            )

        print("-" * 70)
