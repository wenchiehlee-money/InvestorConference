# 2330 TSMC 2026 Q2 Official Materials

Source-Level: primary_company_ir
Official page: https://investor.tsmc.com/chinese/quarterly-results/2026/q2
English page: https://investor.tsmc.com/english/quarterly-results/2026/q2
Checked-At: 2026-07-16
Download-Method: Playwright Chromium browser context + HiNet replay HLS via headed Chromium

## Official Materials

| Material | URL | Local status | Notes |
| :--- | :--- | :--- | :--- |
| Financial Statements | https://investor.tsmc.com/chinese/encrypt/files/encrypt_file/reports/2026-07/114aaca0fea2050e96b91fffbab9ed04ba09cd92/FS.pdf | `data/2330/2330_2026_q2_fs.pdf` / `data/2330/2330_2026_q2_fs.md` | Downloaded by Playwright; PDF magic verified. |
| Presentation Material (TW) | https://investor.tsmc.com/chinese/encrypt/files/encrypt_file/reports/2026-07/2b15e54c7bf8696e0390121adebd2dba48b9d6d5/2Q26%20Presentation%20%28C%29.pdf | `data/2330/2330_2026_q2_ir.pdf` / `data/2330/2330_2026_q2_ir.md` | Downloaded by Playwright; PDF magic verified. |
| Presentation Material (EN) | https://investor.tsmc.com/english/encrypt/files/encrypt_file/reports/2026-07/9ce1ced428b1f53f1319be1fa7964327bcb1b02f/2Q26%20Presentation%20%28E%29.pdf | `data/2330/2330_2026_q2_ir_en.pdf` / `data/2330/2330_2026_q2_ir_en.md` | Downloaded by Playwright; PDF magic verified. |
| Management Report | https://investor.tsmc.com/chinese/encrypt/files/encrypt_file/reports/2026-07/6f49632674bd2d0fd48cb65aaf89ec6ab510b559/2Q26%20ManagementReport.pdf | `data/2330/2330_2026_q2_management_report.pdf` / `data/2330/2330_2026_q2_management_report.md` | Downloaded by Playwright; PDF magic verified. |
| Earnings Release | https://investor.tsmc.com/chinese/encrypt/files/encrypt_file/reports/2026-07/a80d7933be643644081584087731f73b22ea5a2c/2Q26%20EarningsRelease.pdf | `data/2330/2330_2026_q2_earnings_release.pdf` / `data/2330/2330_2026_q2_earnings_release.md` | Downloaded by Playwright; PDF magic verified. |
| Audio/Webcast registration | https://investor.tsmc.com/chinese/form/qr-audio-webcast-registration | submitted via ignored `.env` values | Redirected to official audio-webcast page after registration. |
| Official quarterly page replay | https://ottlive.hinet.net/webapp/tsmc/watch?v=3958 | replay page verified | Official page exposes `線上會議視訊重播`; replay page title is `台積電-影音-台積電2026年第二季法說會(20260716)`. |
| HiNet primary webcast | https://tsmc.hinet.net/tsmc_aw_06152026.html | external webcast page only | Embeds `https://ottlive.hinet.net/webapp/tsmc/liveWindow?layoutMode=pure&channel=14`; backend returned live HLS URL but playlist currently returns 404 and `wordCardType=picture`. |
| HiNet backup webcast | https://tsmc-ott2b2.cdn.hinet.net/tsmc/tsmc_aw_06152026.html | external webcast page only | Embeds `https://ottlive.hinet.net/webapp/tsmc/liveWindow?layoutMode=pure&channel=15`; backend returned live HLS URL but playlist currently returns 404 and `wordCardType=picture`. |
| Teleconference registration | https://investor.tsmc.com/chinese/form/qr-teleconference-registration | no local audio | Current official page is a registration form, not a downloadable replay asset. |

## Download Notes

Direct shell download of official PDFs returned a Cloudflare `Just a moment...` HTML page instead of PDF bytes. Playwright Chromium browser context successfully downloaded the official PDFs and verified `%PDF` magic bytes before saving. README points IR columns to local PDF and MD files.

## Audio / FIN / GT Status

Initial live webcast checks found only ended live channels, but the official quarterly page later exposed replay `https://ottlive.hinet.net/webapp/tsmc/watch?v=3958`.

Replay media was verified through headed Chromium network capture. The effective HLS manifest was `https://tsmcvod-ott2b.cdn.hinet.net/vod_tsmc/_definst_/smil:tsmc/ottliveUpload/video/tsmc/20260716150000_1/hd-hls-cl-pc.smil/playlist.m3u8` with HTTP 200 `application/vnd.apple.mpegurl`; media segments returned HTTP 200 `video/MP2T`. ffmpeg extracted audio-only `data/2330/2330_2026_q2.m4a` from the replay HLS.

Audio validation:

| Field | Value |
| :--- | :--- |
| Local file | `data/2330/2330_2026_q2.m4a` |
| Release URL | https://github.com/wenchiehlee-money/InvestorConference/releases/download/audio-files/2330_2026_q2.m4a |
| Duration | 01:10:25.27 |
| sha256 | `083aee38fce03615dddd874789df4af31693e10e10492354e145ea401e856fdb` |
| Size | 103779169 bytes |
| Codec | AAC LC, 44.1 kHz stereo |
| Source-Level | primary_company_ir_replay |

FIN and GT are still pending. Generate FIN from this verified audio, then generate GT conservatively from FIN plus official IR materials.
