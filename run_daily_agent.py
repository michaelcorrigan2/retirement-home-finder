import traceback

from auto_processor import process_inbox
from send_digest import send_daily_digest
from error_alerts import send_error_alert
from water_review_email import send_water_review_email


def run_daily_agent():
    print()
    print("=" * 70)
    print("RETIREMENT HOME FINDER — DAILY RUN")
    print("=" * 70)

    try:
        print()
        print("STEP 1: Processing new listings...")
        process_inbox()

        print()
        print("STEP 2: Sending any water-review requests...")
        send_water_review_email()

        print()
        print("STEP 3: Building and sending daily digest...")
        send_daily_digest()

        print()
        print("=" * 70)
        print("✅ DAILY AGENT RUN COMPLETE")
        print("=" * 70)

    except Exception:
        error_details = traceback.format_exc()

        print()
        print("=" * 70)
        print("❌ DAILY AGENT FAILED")
        print("=" * 70)
        print(error_details)

        try:
            send_error_alert(error_details)
        except Exception as alert_error:
            print(
                "Could not send error alert:",
                alert_error
            )

        # Important: preserve the failure so Render marks
        # the cron run as failed.
        raise


if __name__ == "__main__":
    run_daily_agent()
