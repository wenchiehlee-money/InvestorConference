# 2330 TSMC 2026 Q2 Official Materials

Source-Level: primary_company_ir
Official page: https://investor.tsmc.com/chinese/quarterly-results/2026/q2
English page: https://investor.tsmc.com/english/quarterly-results/2026/q2
Checked-At: 2026-07-16
Download-Method: Playwright Chromium browser context

## Official Materials

| Material | URL | Local status | Notes |
| :--- | :--- | :--- | :--- |
| Financial Statements | https://investor.tsmc.com/chinese/encrypt/files/encrypt_file/reports/2026-07/114aaca0fea2050e96b91fffbab9ed04ba09cd92/FS.pdf | `data/2330/2330_2026_q2_fs.pdf` / `data/2330/2330_2026_q2_fs.md` | Downloaded by Playwright; PDF magic verified. |
| Presentation Material (TW) | https://investor.tsmc.com/chinese/encrypt/files/encrypt_file/reports/2026-07/8f1aa7a97b70ba94de94d8e46ddc977fca74f918/2Q26%20Presentation%20%28C%29.pdf | `data/2330/2330_2026_q2_ir.pdf` / `data/2330/2330_2026_q2_ir.md` | Downloaded by Playwright; PDF magic verified. |
| Presentation Material (EN) | https://investor.tsmc.com/english/encrypt/files/encrypt_file/reports/2026-07/9ce1ced428b1f53f1319be1fa7964327bcb1b02f/2Q26%20Presentation%20%28E%29.pdf | `data/2330/2330_2026_q2_ir_en.pdf` / `data/2330/2330_2026_q2_ir_en.md` | Downloaded by Playwright; PDF magic verified. |
| Management Report | https://investor.tsmc.com/chinese/encrypt/files/encrypt_file/reports/2026-07/6f49632674bd2d0fd48cb65aaf89ec6ab510b559/2Q26%20ManagementReport.pdf | `data/2330/2330_2026_q2_management_report.pdf` / `data/2330/2330_2026_q2_management_report.md` | Downloaded by Playwright; PDF magic verified. |
| Earnings Release | https://investor.tsmc.com/chinese/encrypt/files/encrypt_file/reports/2026-07/a80d7933be643644081584087731f73b22ea5a2c/2Q26%20EarningsRelease.pdf | `data/2330/2330_2026_q2_earnings_release.pdf` / `data/2330/2330_2026_q2_earnings_release.md` | Downloaded by Playwright; PDF magic verified. |
| Audio/Webcast registration | https://investor.tsmc.com/chinese/form/qr-audio-webcast-registration | no local audio | Current official page is a registration form, not a downloadable replay asset. |
| Teleconference registration | https://investor.tsmc.com/chinese/form/qr-teleconference-registration | no local audio | Current official page is a registration form, not a downloadable replay asset. |

## Download Notes

Direct shell download of official PDFs returned a Cloudflare `Just a moment...` HTML page instead of PDF bytes. Playwright Chromium browser context successfully downloaded the official PDFs and verified `%PDF` magic bytes before saving. README points IR columns to local PDF and MD files.

## Audio / FIN / GT Status

No downloadable official replay audio was found on the official page at check time. Do not generate `2330_2026_q2_FIN.srt` or `2330_2026_q2_GT.srt` until a verified audio/replay source exists or a separate official/third-party transcript source is obtained and clearly marked with source limitations.
