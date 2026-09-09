# InvestorConference Agent Rules

- Never run Whisper, faster-whisper, whisper.cpp, or any other speech-to-text/FIN generation locally in this repository.
- All FIN.srt jobs must use `skills/skill-mlx-api-client-whisper` and the Mac mini MLX issue-driven pipeline.
- Local audio download, HLS decryption, remuxing, ffprobe, and metadata validation are allowed; local speech recognition is not.
- For alphabetic/HK tickers, ensure the Mac mini `company-configs/{TICKER}/whisper.yaml` sets `language: en` before opening `generate-FIN`.
