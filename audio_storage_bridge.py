import json
from pathlib import Path
from audio_storage import AudioStorageClient

def upload_to_gdrive_and_update_manifest(repo: Path, stock_id: str, audio_path: Path):
    client = AudioStorageClient()
    file_id = client.upload_audio(audio_path, stock_id)
    
    manifest_path = repo / "audio_manifest.json"
    manifest = {}
    if manifest_path.exists():
        try: manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except: pass
    
    manifest[audio_path.stem] = file_id
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    audio_path.unlink(missing_ok=True)
    return file_id, manifest_path

def get_audio_link_for_readme(repo: Path, stock_id: str, year: str, quarter: str, audio_min: float):
    stem = f"{stock_id}_{year}_q{quarter}"
    manifest_path = repo / "audio_manifest.json"
    dur_str = f"{audio_min:.1f} min" if audio_min else "無"
    
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if stem in manifest:
                return f"[{dur_str}](https://drive.google.com/uc?export=download&id={manifest[stem]})"
        except: pass
    return dur_str
