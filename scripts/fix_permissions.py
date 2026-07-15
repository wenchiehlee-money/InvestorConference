import json
import os
from pathlib import Path
from audio_storage import AudioStorageClient
from dotenv import load_dotenv

load_dotenv()

def fix_all_permissions():
    manifest_path = Path("audio_manifest.json")
    if not manifest_path.exists():
        print("Manifest not found")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    client = AudioStorageClient()
    print(f"Fixing permissions for {len(manifest)} files...")

    for stem, file_id in manifest.items():
        try:
            client.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            print(f"✓ Fixed: {stem} ({file_id})")
        except Exception as e:
            print(f"✗ Failed: {stem} - {e}")

if __name__ == "__main__":
    fix_all_permissions()
