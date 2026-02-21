#!/usr/bin/env python3
"""
scripts/drive_setup.py
-----------------------
ONE-TIME host-machine setup script for Google Drive auth.

Run this on your Windows machine (NOT inside Docker):
    python scripts/drive_setup.py

What it does:
  1. Reads auth/credentials.json (downloaded from Google Cloud Console)
  2. Opens your browser for Google OAuth consent
  3. Saves auth/token.json — the container will use this for all Drive operations

You only need to run this once. The token auto-refreshes silently after that.

Prerequisites:
  pip install google-api-python-client google-auth-oauthlib
  Place your credentials.json at: auth/credentials.json
"""

import sys
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Missing dependencies. Run on your host machine:")
    print("  pip install google-api-python-client google-auth-oauthlib")
    sys.exit(1)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = PROJECT_ROOT / "auth" / "credentials.json"
TOKEN_PATH = PROJECT_ROOT / "auth" / "token.json"


def main():
    print("=" * 55)
    print("  Google Drive Auth Setup — Resume Editor")
    print("=" * 55)
    print()

    # Check credentials.json exists
    if not CREDENTIALS_PATH.exists():
        print("ERROR: credentials.json not found.")
        print()
        print("Please complete these steps first:")
        print("  1. Go to https://console.cloud.google.com")
        print("  2. Create a project and enable the Google Drive API")
        print("  3. Create OAuth2 credentials (type: Desktop App)")
        print("  4. Download the JSON and save it to:")
        print(f"       {CREDENTIALS_PATH}")
        print()
        sys.exit(1)

    # Check if already authenticated
    if TOKEN_PATH.exists():
        print(f"Token already exists at: {TOKEN_PATH}")
        answer = input("Re-authenticate? [y/N]: ").strip().lower()
        if answer != "y":
            print("Skipping. Existing token will be used.")
            sys.exit(0)

    # Run OAuth flow (opens browser)
    print("Opening browser for Google consent...")
    print("(If browser doesn't open, check the URL printed below)\n")
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
    creds = flow.run_local_server(port=0)

    # Save token
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    print()
    print(f"✓ Token saved to: {TOKEN_PATH}")

    # Quick smoke test — list Drive root
    print("\nVerifying connection to Google Drive...")
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    about = service.about().get(fields="user").execute()
    user = about.get("user", {})
    print(f"✓ Connected as: {user.get('displayName')}  ({user.get('emailAddress')})")
    print()
    print("Setup complete! You can now run the Docker-based pipeline.")
    print("The container will pick up auth/token.json automatically.")


if __name__ == "__main__":
    main()
