import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

from dotenv import load_dotenv


load_dotenv(".env")

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
YOUR_EMAIL = os.getenv("YOUR_EMAIL")


def send_error_alert(error_text):
    if not all([
        GMAIL_ADDRESS,
        GMAIL_APP_PASSWORD,
        YOUR_EMAIL
    ]):
        print("Error alert email not configured.")
        return

    message = EmailMessage()

    message["From"] = GMAIL_ADDRESS
    message["To"] = YOUR_EMAIL
    message["Subject"] = "⚠️ Retirement Home Finder Error"

    timestamp = datetime.now().strftime(
        "%B %d, %Y at %I:%M %p"
    )

    message.set_content(
        f"""
Retirement Home Finder encountered an error.

Time:
{timestamp}

Error:
{error_text}

The daily search may not have completed successfully.

Check the Render logs for more information.
""".strip()
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

    print("⚠️ Error alert email sent.")


if __name__ == "__main__":
    send_error_alert(
        "TEST ERROR — the alert system is working."
    )
