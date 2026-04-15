import os
import json
from audio_utils import audio_mgr, ENV

def sync():
    # 1. 取得雲端資料夾內容
    folder_id = ENV.get("GDRIVE_AUDIO_FOLDER_ID")
    if not folder_id:
        print("GDRIVE_AUDIO_FOLDER_ID not found in .env")
        return

    print(f"Checking Google Drive folder: {folder_id}...")
    try:
        results = audio_mgr.service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="files(id, name, size)",
            pageSize=100
        ).execute()
        drive_files = results.get('files', [])
        print(f"Found {len(drive_files)} files in Google Drive.")

        # 2. 同步至 Manifest
        updated_count = 0
        for d_file in drive_files:
            found = False
            for m_item in audio_mgr.manifest:
                if m_item['file_name'] == d_file['name']:
                    m_item['drive_id'] = d_file['id']
                    if 'size' in d_file:
                        m_item['size_mb'] = round(int(d_file['size']) / (1024*1024), 2)
                    updated_count += 1
                    found = True
                    break
            
            if not found:
                audio_mgr.manifest.append({
                    'file_name': d_file['name'],
                    'drive_id': d_file['id'],
                    'size_mb': round(int(d_file.get('size', 0)) / (1024*1024), 2)
                })
                updated_count += 1

        audio_mgr._save_manifest()
        print(f"Success! Updated {updated_count} IDs in audio_manifest.json.")

        # 3. Check for missing
        missing = [m['file_name'] for m in audio_mgr.manifest if not m.get('drive_id')]
        if missing:
            print(f"Warning: {len(missing)} files still missing on Drive: {missing}")
        else:
            print("All LFS files are now synced with Google Drive.")

    except Exception as e:
        print(f"Sync failed: {e}")

if __name__ == "__main__":
    sync()
