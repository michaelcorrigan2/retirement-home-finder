from auto_processor import process_inbox
from send_digest import send_daily_digest


def run_daily_agent():
    print()
    print("=" * 70)
    print("RETIREMENT HOME FINDER — DAILY RUN")
    print("=" * 70)

    print()
    print("STEP 1: Processing new listings...")
    process_inbox()

    print()
    print("STEP 2: Building and sending daily digest...")
    send_daily_digest()

    print()
    print("=" * 70)
    print("✅ DAILY AGENT RUN COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_daily_agent()
