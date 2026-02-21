"""
src/auth.py
-----------
Auth abstraction layer for Google Drive credentials.

TODAY  (single-user CLI):  get_credentials(token_path="auth/token.json")
PHASE 5 (multi-user web):  get_credentials(token_dict=user.drive_token)

Only this file needs to change when moving to per-user auth.
DriveUploader and all scripts just call get_credentials() and pass
the returned `creds` object — they never touch files or tokens directly.
"""

from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_credentials(
    token_path: str | Path | None = None,
    token_dict: dict | None = None,
    credentials_path: str | Path | None = None,
):
    """
    Return a valid google.oauth2.credentials.Credentials object.

    Args:
        token_path:       Path to a token.json file (single-user / CLI mode).
        token_dict:       A dict with token fields (Phase 5 multi-user mode —
                          pass the user's stored token from DB/session).
        credentials_path: Path to credentials.json (only needed when
                          token_path is given and token doesn't exist yet,
                          i.e. first-run desktop auth — handled by drive_setup.py).

    Returns:
        google.oauth2.credentials.Credentials

    Raises:
        FileNotFoundError: if token_path given but file doesn't exist.
        ValueError:        if neither token_path nor token_dict provided.
    """
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
    except ImportError:
        raise ImportError(
            "Google auth libraries not installed. Run: "
            "pip install google-api-python-client google-auth-oauthlib"
        )

    # ----------------------------------------------------------------
    # Mode A: token_dict provided (Phase 5 — per-user from DB/session)
    # ----------------------------------------------------------------
    if token_dict is not None:
        creds = Credentials.from_authorized_user_info(token_dict, SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds

    # ----------------------------------------------------------------
    # Mode B: token_path provided (today — single-user file-based)
    # ----------------------------------------------------------------
    if token_path is not None:
        token_path = Path(token_path)
        if not token_path.exists():
            raise FileNotFoundError(
                f"Drive token not found at '{token_path}'.\n"
                "Run  python scripts/drive_setup.py  on your host machine "
                "to authenticate and generate the token file."
            )
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Persist refreshed token back to file
            token_path.write_text(creds.to_json(), encoding="utf-8")
        return creds

    raise ValueError("Provide either token_path or token_dict to get_credentials().")


def default_credentials():
    """
    Convenience wrapper that uses the project-default token path.
    Used by CLI scripts so they don't need to know the path.

    Returns None (silently) if the token file doesn't exist —
    callers should handle None gracefully to avoid crashing builds.
    """
    project_root = Path(__file__).resolve().parent.parent
    token_path = project_root / "auth" / "token.json"
    try:
        return get_credentials(token_path=token_path)
    except FileNotFoundError:
        return None
    except Exception:
        return None
