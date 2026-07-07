#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_ir_pdfs.py — 批次將各股票資料夾中的 *.pdf 轉為 *.md

轉錄一律透過 skills/mac-mini-ocr 技能（與其他 repo 的用法一致）：
- Mac-mini OCR API 在線 → 完整 OCR 轉錄（ocr_client）
- 離線或失敗 → 本地文字層抽取（pdf_fallback），無文字層的掃描頁會插入
  TODO:OCR 標記，之後可用以下指令補轉錄：

      python skills/mac-mini-ocr/scripts/refine_todo_ocr.py <md檔> --pdf <pdf檔>

使用方式：
    python scripts/convert_ir_pdfs.py             # 掃描全部股票資料夾
    python scripts/convert_ir_pdfs.py 2301 DELL   # 只處理指定資料夾
"""
import platform
import sys
from pathlib import Path

from dotenv import load_dotenv

# Enforce UTF-8 console output for Chinese characters
if platform.system() == 'Windows':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

# 透過 skills/mac-mini-ocr 技能進行轉錄
SKILL_SCRIPTS = REPO_ROOT / "skills" / "mac-mini-ocr" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
from ocr_client import transcribe_document_to_markdown  # noqa: E402
from pdf_fallback import extract_pdf_to_markdown  # noqa: E402

def is_company_dir(path):
    if not path.is_dir():
        return False
    name = path.name
    if name in (".git", ".github", ".claude", "__pycache__", "definitions", "spec", "tmp", "tools", "web", "logs", "scripts", "skills"):
        return False
    return name.isdigit() or (name.isupper() and name.isalpha())

def is_valid_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as f:
            return f.read(5) == b"%PDF-"
    except Exception:
        return False

def convert_pdf_to_md(pdf_path, md_path):
    print(f"Converting {pdf_path.name} -> {md_path.name}...")

    if not is_valid_pdf(pdf_path):
        print(f"  [INVALID PDF] {pdf_path.name} 內容不是 PDF（可能是下載失敗的 HTML 錯誤頁），請重新下載")
        return False

    # 先嘗試 Mac-mini OCR API
    try:
        md_text = transcribe_document_to_markdown(pdf_path, dpi=200)
        if md_text:
            md_path.write_text(md_text, encoding="utf-8")
            print(f"  [OCR SUCCESS] Saved {md_path.name} (Chars: {len(md_text)})")
            return True
        print("  [OCR EMPTY] API 回傳空白內容，改用本地退援抽取...")
    except Exception as e:
        print(f"  [OCR UNAVAILABLE] {e}")
        print("  改用 pdf_fallback 本地文字層抽取（掃描頁將標記 TODO:OCR）...")

    # 退援：本地文字層抽取（無文字層的頁面插入 TODO:OCR 標記）
    try:
        fallback_md = extract_pdf_to_markdown(pdf_path)
        md_path.write_text(fallback_md, encoding="utf-8")
        print(f"  [FALLBACK SUCCESS] Saved {md_path.name}；含 TODO:OCR 標記的頁面可於 Mac-mini 恢復後以 refine_todo_ocr.py 補轉錄")
        return True
    except Exception as e:
        print(f"  [FALLBACK FAILED] {e}")
        return False

def main():
    print("=== Converting Investor Presentation PDFs to Markdown (via skills/mac-mini-ocr) ===")
    targets = set(sys.argv[1:])
    company_dirs = [d for d in REPO_ROOT.iterdir() if is_company_dir(d)]
    if targets:
        company_dirs = [d for d in company_dirs if d.name in targets]
        unknown = targets - {d.name for d in company_dirs}
        if unknown:
            print(f"警告：找不到資料夾 {sorted(unknown)}")

    converted_count = 0
    skipped_count = 0
    failed_count = 0

    for c_dir in sorted(company_dirs):
        for file in sorted(c_dir.iterdir()):
            if file.is_file() and file.name.endswith(".pdf"):
                md_path = c_dir / f"{file.stem}.md"

                # Check if MD already exists
                if md_path.exists():
                    skipped_count += 1
                    continue

                if convert_pdf_to_md(file, md_path):
                    converted_count += 1
                else:
                    failed_count += 1

    print(f"\nFinished! Converted: {converted_count}, Already Exists (Skipped): {skipped_count}, Failed: {failed_count}")
    return 1 if failed_count else 0

if __name__ == "__main__":
    sys.exit(main())
