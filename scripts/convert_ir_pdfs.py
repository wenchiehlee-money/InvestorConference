import os
import sys
import requests
import platform
from pathlib import Path
from pypdf import PdfReader
from dotenv import load_dotenv

# Enforce UTF-8 console output for Chinese characters
if platform.system() == 'Windows':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

def is_company_dir(path):
    if not path.is_dir():
        return False
    name = path.name
    if name in (".git", ".github", ".claude", "__pycache__", "definitions", "spec", "tmp", "tools", "web", "logs", "scripts"):
        return False
    return name.isdigit() or (name.isupper() and name.isalpha())

def extract_text_directly(pdf_path):
    """
    Fallback pypdf text extraction logic.
    """
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        for idx, page in enumerate(reader.pages):
            text_parts.append(f"## Page {idx + 1}\n")
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text + "\n")
            else:
                text_parts.append("*(No text extracted from this page)*\n")
        return "\n".join(text_parts)
    except Exception as e:
        print(f"  Fallback direct extract failed: {e}")
        return ""

def convert_pdf_to_md(pdf_path, md_path):
    print(f"Converting {pdf_path.name} -> {md_path.name}...")
    
    # Check if OCR server is configured
    api_url = os.getenv("OCR_API_URL", "http://mac-mini.tail28f10.ts.net:5001/ocr")
    api_key = os.getenv("OCR_API_KEY")
    
    if api_key:
        try:
            print(f"  Sending to Mac-mini OCR API: {api_url}")
            headers = {"X-API-Key": api_key}
            with open(pdf_path, "rb") as f:
                files = {"file": (pdf_path.name, f, "application/octet-stream")}
                data = {"dpi": "200"}
                # High timeout since OCR on full PDFs takes time
                response = requests.post(api_url, headers=headers, files=files, data=data, timeout=900)
                
            if response.status_code == 200:
                md_text = response.json().get("markdown", "")
                if md_text:
                    md_path.write_text(md_text, encoding="utf-8")
                    print(f"  [OCR SUCCESS] Saved {md_path.name} (Chars: {len(md_text)})")
                    return True
            print(f"  [OCR FAILED] Status code {response.status_code}. Falling back to direct text extraction...")
        except Exception as e:
            print(f"  [OCR ERROR] {e}. Falling back to direct text extraction...")
    else:
        print("  [OCR CONFIG] OCR_API_KEY not found in environment. Using fallback text extraction...")
        
    # Fallback direct extraction
    full_text = extract_text_directly(pdf_path)
    if full_text:
        # If very little text is extracted, mark it as TODO:OCR
        clean_text = "".join([c for c in full_text if c.isalnum()])
        if len(clean_text) < 100:
            full_text = "TODO:OCR\n\n" + full_text
            
        md_path.write_text(full_text, encoding="utf-8")
        print(f"  [DIRECT SUCCESS] Saved {md_path.name} (Chars: {len(full_text)})")
        return True
        
    return False

def main():
    print("=== Converting Investor Presentation PDFs to Markdown ===")
    company_dirs = [d for d in REPO_ROOT.iterdir() if is_company_dir(d)]
    
    converted_count = 0
    skipped_count = 0
    
    for c_dir in company_dirs:
        for file in c_dir.iterdir():
            if file.is_file() and file.name.endswith(".pdf"):
                stem = file.stem
                md_name = f"{stem}.md"
                md_path = c_dir / md_name
                
                # Check if MD already exists
                if md_path.exists():
                    skipped_count += 1
                    continue
                
                # Convert PDF to MD
                success = convert_pdf_to_md(file, md_path)
                if success:
                    converted_count += 1
                    
    print(f"\nFinished! Converted: {converted_count}, Already Exists (Skipped): {skipped_count}")

if __name__ == "__main__":
    main()
