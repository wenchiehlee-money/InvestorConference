import os
import sys
from pathlib import Path
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')
REPO_ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS = REPO_ROOT

def is_company_dir(path):
    if not path.is_dir():
        return False
    name = path.name
    if name in (".git", ".github", ".claude", "__pycache__", "definitions", "spec", "tmp", "tools", "web", "logs", "scripts"):
        return False
    return name.isdigit() or (name.isupper() and name.isalpha())

def convert_pdf_to_md(pdf_path, md_path):
    print(f"Converting {pdf_path.name} -> {md_path.name}...")
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
        
        full_text = "\n".join(text_parts)
        # If very little text is extracted, mark it as TODO:OCR
        clean_text = "".join([c for c in full_text if c.isalnum()])
        if len(clean_text) < 100:
            full_text = "TODO:OCR\n\n" + full_text
            
        md_path.write_text(full_text, encoding="utf-8")
        print(f"  Saved {md_path.name} (Chars: {len(full_text)})")
        return True
    except Exception as e:
        print(f"  Error converting {pdf_path.name}: {e}")
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
