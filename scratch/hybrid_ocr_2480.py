import os
import sys
import time
import tempfile
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from dotenv import load_dotenv

# Enforce UTF-8 for console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Load dotenv
load_dotenv()

# Add skills/mac-mini-ocr/scripts to path to import ocr_client
sys.path.append(r"C:\Users\WJLEE\.gemini\antigravity-cli\skills\mac-mini-ocr\scripts")
import ocr_client

# Pages that need high-precision OCR (1-indexed)
PAGES_TO_OCR = {26, 27, 28, 29, 30, 31, 32, 33, 37, 38, 40, 41, 42, 43}

def extract_direct_page_text(pdf_path: Path, page_idx: int) -> str:
    """Extract text directly from a single page using pypdf."""
    try:
        reader = PdfReader(pdf_path)
        page_text = reader.pages[page_idx].extract_text()
        return page_text if page_text else ""
    except Exception as e:
        print(f"  [Direct-Extract] Failed on Page {page_idx+1}: {e}")
        return ""

def ocr_single_page_robust(pdf_path: Path, page_idx: int, temp_dir: Path, dpi: int = 200) -> str:
    """Extract page, save to temp pdf, call Mac-mini OCR, with retries."""
    single_pdf = temp_dir / f"page_{page_idx + 1}.pdf"
    
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        writer.add_page(reader.pages[page_idx])
        with open(single_pdf, "wb") as f:
            writer.write(f)
            
        max_retries = 5
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                print(f"  [OCR] Calling Mac-mini for Page {page_idx+1} (Attempt {attempt+1}/{max_retries})...")
                md_text = ocr_client.transcribe_document_to_markdown(single_pdf, dpi=dpi)
                return md_text
            except Exception as e:
                print(f"  [OCR ERROR] Attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"  [OCR] Waiting {retry_delay}s before retry...")
                    time.sleep(retry_delay)
                else:
                    raise e
    except Exception as e:
        print(f"  [CRITICAL OCR FAIL] Page {page_idx+1}: {e}")
        return f"*(OCR Failed for this page: {e})*\nTODO:OCR\n"
    finally:
        single_pdf.unlink(missing_ok=True)

def process_pdf(input_pdf: Path, output_md: Path):
    print(f"\n================ Processing {input_pdf.name} ================")
    if not input_pdf.exists():
        print(f"Error: {input_pdf} does not exist.")
        return

    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")
    
    assembled_parts = []
    
    with tempfile.TemporaryDirectory(prefix="mmo_hybrid_") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        
        for i in range(total_pages):
            page_num = i + 1
            print(f"Processing Page {page_num}/{total_pages}...")
            
            # Check if this page requires OCR
            needs_ocr = page_num in PAGES_TO_OCR
            page_content = ""
            
            if not needs_ocr:
                # Try direct text extraction first
                direct_txt = extract_direct_page_text(input_pdf, i)
                clean_len = len("".join([c for c in direct_txt if c.isalnum()]))
                if clean_len >= 100:
                    page_content = direct_txt
                    print(f"  [Direct] Extracted {clean_len} alphanumeric chars.")
                else:
                    print(f"  [Fallback] Low density ({clean_len} chars). Triggering OCR.")
                    needs_ocr = True
            
            if needs_ocr:
                page_content = ocr_single_page_robust(input_pdf, i, temp_dir)
                time.sleep(2.0) # cool down GPU
                
            assembled_parts.append(f"## Page {page_num}\n\n{page_content}\n")
            
    final_md = "\n".join(assembled_parts)
    output_md.write_text(final_md, encoding="utf-8")
    print(f"[SUCCESS] Wrote to {output_md}")

def main():
    repo = Path(r"C:\Users\WJLEE\SynologyDrive\NAS\github.com\InvestorConference")
    
    # 2480 Q1 Chinese PDF
    pdf_zh = repo / "2480" / "2480_2026_q1_ir.pdf"
    md_zh = repo / "2480" / "2480_2026_q1_ir.md"
    process_pdf(pdf_zh, md_zh)
    
    # 2480 Q1 English PDF
    pdf_en = repo / "2480" / "2480_2026_q1_ir_en.pdf"
    md_en = repo / "2480" / "2480_2026_q1_ir_en.md"
    process_pdf(pdf_en, md_en)

if __name__ == "__main__":
    main()
