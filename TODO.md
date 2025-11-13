# TODO

## Priority

- [ ] Test subtitle parser with real anime files from different sources
- [ ] Add better error messages for file upload failures
- [X] Python backend setup with MeCab/fugashi
- [X] Connect Next.js API to Python service
- [X] FastAPI server implementation
- [X] MeCab tokenization endpoint
- [X] JLPT level detection algorithm
- [X] Grammar pattern database and detection
- [X] Vocabulary extraction with French translations
- [X] AI explanation feature (OpenRouter/Gemini)

## Features

- [X] Anki export functionality via AnkiConnect - **Completed**
  - [X] AnkiConnect integration
  - [X] Customizable deck and model selection
  - [X] Vocabulary selection before export
  - [X] Grammar and translation options
- [ ] Add download button for analyzed sentences (JSON/CSV)
- [ ] Save analysis results to localStorage
- [ ] User authentication (Supabase)
- [ ] Progress tracking dashboard

## UI/UX

- [ ] Better loading states
- [ ] Toast notifications instead of alerts
- [ ] Dark mode support
- [ ] Mobile responsiveness improvements
- [ ] Add keyboard shortcuts

## Later

- [ ] Add more JLPT vocab databases (expand coverage)
- [ ] Support for more subtitle formats (.vtt) - **In progress**
- [ ] Audio playback integration
- [ ] Sentence difficulty filtering
- [ ] Export to CSV
- [ ] Batch processing for large subtitle files

## Maybe

- [ ] Mobile app version?
- [ ] Chrome extension for streaming sites?
- [ ] Community sharing features
- [ ] Gamification elements

## Bugs to Fix

- [ ] None yet (fingers crossed)

## Notes

- ✅ Backend is fully functional with real NLP analysis
- Need to test with actual anime subtitles from different sources
- Consider rate limiting for API if deploying publicly
- Look into caching analyzed sentences (backend already has translation cache)
- AI explanations are cached for 24h to save API quota
