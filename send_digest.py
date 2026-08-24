import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

from dotenv import load_dotenv
from daily_digest import build_digest


load_dotenv(dotenv_path=".env")

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


def send_daily_digest():
    digest = build_digest()

    today = datetime.now().strftime("%B %d, %Y")

    message = EmailMessage()

    message["From"] = GMAIL_ADDRESS
    message["To"] = ", ".join(RECIPIENTS)
    message["Subject"] = (
        f"Retirement Home Matches — {today}"
    )

    message.set_content(digest)

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
    print()

    for recipient in RECIPIENTS:
        print(f"- {recipient}")


if __name__ == "__main__":
    send_daily_digest()
