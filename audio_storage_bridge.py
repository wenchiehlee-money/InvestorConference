import json
import os
import requests
from pathlib import Path
from audio_storage import AudioStorageClient

_REPO = "wenchiehlee-money/InvestorConference"
_GH_RELEASE_TAG = "audio-files"


def _get_or_create_gh_release(token: str) -> dict:
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    base = f"https://api.github.com/repos/{_REPO}"

    r = requests.get(f"{base}/releases/tags/{_GH_RELEASE_TAG}", headers=headers)
    if r.status_code == 200:
        return r.json()

    r = requests.post(f"{base}/releases", headers=headers, json={
        "tag_name": _GH_RELEASE_TAG,
        "name": "Audio Files",
        "body": "Investor conference call audio files (CORS-friendly streaming).",
        "draft": False,
        "prerelease": False,
    })
    r.raise_for_status()
    return r.json()


def _upload_gh_asset(release: dict, token: str, audio_path: Path) -> str:
    # Return existing asset URL if already uploaded
    for asset in release.get("assets", []):
        if asset["name"] == audio_path.name:
            print(f"[gh-release] Asset already exists: {asset['browser_download_url']}")
            return asset["browser_download_url"]

    content_type = "audio/mp4" if audio_path.suffix == ".m4a" else "audio/mpeg"
    headers = {"Authorization": f"token {token}", "Content-Type": content_type}
    upload_url = release["upload_url"].replace("{?name,label}", f"?name={audio_path.name}")

    with open(audio_path, "rb") as f:
        r = requests.post(upload_url, headers=headers, data=f)
        r.raise_for_status()

    url = r.json()["browser_download_url"]
    print(f"[gh-release] Uploaded: {url}")
    return url


def upload_to_gdrive_and_update_manifest(repo: Path, stock_id: str, audio_path: Path):
    client = AudioStorageClient()
    file_id = client.upload_audio(audio_path, stock_id)

    manifest_path = repo / "audio_manifest.json"
    manifest = {}
    if manifest_path.exists():
        try: manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except: pass

    # Prefer GitHub Releases URL (CORS-friendly) over bare GDrive ID
    gh_token = os.environ.get("GITHUB_TOKEN")
    if gh_token:
        try:
            release = _get_or_create_gh_release(gh_token)
            manifest[audio_path.stem] = _upload_gh_asset(release, gh_token, audio_path)
        except Exception as e:
            print(f"[gh-release] Upload failed, falling back to GDrive ID: {e}")
            manifest[audio_path.stem] = file_id
    else:
        print("[gh-release] GITHUB_TOKEN not set, storing GDrive ID in manifest")
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
                val = manifest[stem]
                # Full URL (GitHub Release) or legacy GDrive ID
                url = val if val.startswith("https://") else f"https://drive.google.com/uc?export=download&id={val}"
                return f"[{dur_str}]({url})"
        except: pass
    return dur_str
