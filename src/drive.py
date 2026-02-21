"""
src/drive.py
------------
Google Drive uploader. Works for any user — credentials are injected,
never read from files directly (that's auth.py's job).

Usage:
    from src.auth import default_credentials
    from src.drive import DriveUploader

    creds = default_credentials()
    uploader = DriveUploader(creds)
    link = uploader.upload_pdf(Path("output/Aryan_PI_2602.pdf"), meta_code="PI")
    print(link)
"""

from pathlib import Path


RESUME_ROOT_FOLDER = "Resume"


class DriveUploader:
    def __init__(self, creds):
        """
        Args:
            creds: google.oauth2.credentials.Credentials
                   (returned by src.auth.get_credentials or default_credentials)
        """
        try:
            from googleapiclient.discovery import build
        except ImportError:
            raise ImportError(
                "Google API client not installed. Run: "
                "pip install google-api-python-client google-auth-oauthlib"
            )
        self.service = build("drive", "v3", credentials=creds, cache_discovery=False)
        self._folder_cache: dict[str, str] = {}   # name -> folder_id

    # ----------------------------------------------------------------
    # Folder helpers
    # ----------------------------------------------------------------

    def get_or_create_folder(self, name: str, parent_id: str | None = None) -> str:
        """
        Return the Drive folder ID for `name` inside `parent_id`.
        Creates the folder if it doesn't exist. Idempotent.
        """
        cache_key = f"{parent_id}:{name}"
        if cache_key in self._folder_cache:
            return self._folder_cache[cache_key]

        # Search for an existing folder with this name + parent
        query = (
            f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
            " and trashed=false"
        )
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = (
            self.service.files()
            .list(q=query, spaces="drive", fields="files(id, name)")
            .execute()
        )
        files = results.get("files", [])

        if files:
            folder_id = files[0]["id"]
        else:
            # Create the folder
            meta = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            if parent_id:
                meta["parents"] = [parent_id]
            folder = self.service.files().create(body=meta, fields="id").execute()
            folder_id = folder["id"]

        self._folder_cache[cache_key] = folder_id
        return folder_id

    def ensure_structure(self, meta_code: str) -> str:
        """
        Ensure  My Drive → Resume/ → Resume/<meta_code>/  exists.
        Returns the ID of the Resume/<meta_code> subfolder.
        """
        root_id = self.get_or_create_folder(RESUME_ROOT_FOLDER)
        sub_id = self.get_or_create_folder(meta_code.upper(), parent_id=root_id)
        return sub_id

    # ----------------------------------------------------------------
    # Upload
    # ----------------------------------------------------------------

    def _find_existing_file(self, filename: str, parent_id: str) -> str | None:
        """Return file ID if a file with `filename` already exists in `parent_id`."""
        query = (
            f"name='{filename}' and '{parent_id}' in parents and trashed=false"
        )
        results = (
            self.service.files()
            .list(q=query, spaces="drive", fields="files(id)")
            .execute()
        )
        files = results.get("files", [])
        return files[0]["id"] if files else None

    def upload_pdf(self, pdf_path: Path, meta_code: str) -> str:
        """
        Upload a PDF to  My Drive/Resume/<meta_code>/.
        If a file with the same name already exists there, it is replaced.

        Returns:
            A shareable Google Drive view link for the uploaded file.
        """
        try:
            from googleapiclient.http import MediaFileUpload
        except ImportError:
            raise ImportError("Install google-api-python-client")

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        folder_id = self.ensure_structure(meta_code)
        filename = pdf_path.name
        media = MediaFileUpload(str(pdf_path), mimetype="application/pdf", resumable=True)

        existing_id = self._find_existing_file(filename, folder_id)

        if existing_id:
            # Update existing file (keeps same ID / share link)
            file = (
                self.service.files()
                .update(
                    fileId=existing_id,
                    media_body=media,
                    fields="id, webViewLink",
                )
                .execute()
            )
            file_id = existing_id
        else:
            # Create new file
            meta = {"name": filename, "parents": [folder_id]}
            file = (
                self.service.files()
                .create(
                    body=meta,
                    media_body=media,
                    fields="id, webViewLink",
                )
                .execute()
            )
            file_id = file["id"]

        # Make the file viewable by anyone with the link
        try:
            self.service.permissions().create(
                fileId=file_id,
                body={"type": "anyone", "role": "reader"},
                fields="id"
            ).execute()
        except Exception as e:
            print(f"  [Warning] Could not set public permissions: {e}")

        return file.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view")
