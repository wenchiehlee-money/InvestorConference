import os
import json
import re
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from io import FileIO
import io

# Load environment variables (supports simple .env format)
def load_env():
    # Search for .env in current and parent directories
    current = Path(__file__).resolve().parent
    for _ in range(3): # check up to 3 parent levels
        path = current / ".env"
        if path.exists():
            print(f"Loading environment from {path}")
            env = {}
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        env[key.strip()] = value.strip().strip('"').strip("'")
            return env
        current = current.parent
    return {}

ENV = load_env()
GDRIVE_API_CREDENTIALS = ENV.get("GDRIVE_API_CREDENTIALS")
GDRIVE_AUDIO_FOLDER_ID = ENV.get("GDRIVE_AUDIO_FOLDER_ID")

class AudioLoader:
    def __init__(self):
        self.service = self._init_service()
        self.manifest_path = Path(__file__).parent / "audio_manifest.json"
        self.manifest = self._load_manifest()

    def _init_service(self):
        if not GDRIVE_API_CREDENTIALS:
            print("Warning: GDRIVE_API_CREDENTIALS not found in .env")
            return None
        try:
            # Parse JSON string from .env
            info = json.loads(GDRIVE_API_CREDENTIALS)
            credentials = service_account.Credentials.from_service_account_info(info)
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            print(f"Error initializing Google Drive service: {e}")
            return None

    def _load_manifest(self):
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_manifest(self):
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=4, ensure_ascii=False)

    def get_audio_path(self, stock_id, year, quarter):
        """Transparently get the path to an audio file."""
        filename = f"{stock_id}_{year}_q{quarter}.m4a"
        
        # 1. Check local path (relative to repo root)
        local_path = Path(__file__).parent / stock_id / filename
        if local_path.exists():
            return str(local_path)
        
        # 2. Check cache directory (tmp/)
        cache_path = Path(__file__).parent / "tmp" / filename
        if cache_path.exists():
            return str(cache_path)
            
        # 3. Download from Google Drive if available
        for item in self.manifest:
            if item['file_name'] == filename and item.get('drive_id'):
                print(f"Downloading {filename} from Google Drive...")
                return self.download_from_drive(item['drive_id'], cache_path)
        
        print(f"Audio file {filename} not found locally or on Drive.")
        return None

    def download_from_drive(self, drive_id, dest_path):
        if not self.service: return None
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        request = self.service.files().get_media(fileId=drive_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            
        with open(dest_path, 'wb') as f:
            f.write(fh.getvalue())
        return str(dest_path)

    def upload_to_drive(self, local_path):
        """Upload a file and update manifest."""
        if not self.service or not GDRIVE_AUDIO_FOLDER_ID:
            print("Upload failed: Missing credentials or Folder ID.")
            return None
            
        local_path = Path(local_path)
        if not local_path.exists():
            return None
            
        file_metadata = {
            'name': local_path.name,
            'parents': [GDRIVE_AUDIO_FOLDER_ID]
        }
        
        # 使用 resumable=True 並確保支援大型檔案上傳
        media = MediaFileUpload(str(local_path), resumable=True, chunksize=1024*1024)
        
        try:
            # 建立檔案
            file = self.service.files().create(
                body=file_metadata, 
                media_body=media, 
                fields='id'
            ).execute()
            drive_id = file.get('id')
            
            # 更新 manifest
            found = False
            for item in self.manifest:
                if item['file_name'] == local_path.name:
                    item['drive_id'] = drive_id
                    found = True
                    break
            if not found:
                # 取得檔案資訊
                match = re.search(r'(\w+)_(\d{4})_q(\d)', local_path.name)
                self.manifest.append({
                    'file_name': local_path.name,
                    'drive_id': drive_id,
                    'size_mb': round(os.path.getsize(local_path) / (1024*1024), 2),
                    'company': match.group(1) if match else 'unknown',
                    'year': match.group(2) if match else 'unknown',
                    'quarter': match.group(3) if match else 'unknown',
                    'relative_path': str(local_path.relative_to(Path(__file__).parent)).replace('\\', '/')
                })
            self._save_manifest()
            return drive_id
        except Exception as e:
            if "storageQuotaExceeded" in str(e):
                print(f"Error: The Service Account reached its internal quota. This is common. Trying to use Folder ID {GDRIVE_AUDIO_FOLDER_ID}")
            raise e

# Instantiate shared loader
audio_mgr = AudioLoader()

if __name__ == "__main__":
    # Test/Utility CLI
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "upload":
        audio_mgr.upload_to_drive(sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == "migrate":
        # Migrate all files in manifest that don't have drive_id
        for item in audio_mgr.manifest:
            if not item.get('drive_id'):
                p = Path(__file__).parent / item['relative_path']
                if p.exists():
                    print(f"Migrating {p.name}...")
                    audio_mgr.upload_to_drive(p)
