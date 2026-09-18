# Anime Quote Analyzer

Full-stack Japanese subtitle analysis tool built for language learning.

The application parses anime subtitle files (`.srt`, `.ass`), analyzes Japanese text with a Python NLP backend, estimates JLPT difficulty, detects grammar patterns, extracts vocabulary, and can export selected items to Anki.

## What it does

- Parses `.srt` and `.ass` subtitle files.
- Tokenizes Japanese text with MeCab / fugashi.
- Estimates JLPT level from N5 to N1.
- Detects grammar patterns and extracts vocabulary.
- Provides French translations and optional AI-generated explanations.
- Exports selected vocabulary to Anki through AnkiConnect.
- Provides a responsive drag-and-drop interface.

## Architecture

**Frontend**
- Next.js 14 / App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- Framer Motion

**Backend**
- Python
- FastAPI
- MeCab / fugashi
- JLPT classification
- Grammar detection
- Translation service
- Optional AI explanations through OpenRouter or Gemini

The frontend calls the FastAPI service for Japanese NLP analysis. AI explanations are optional and configured through environment variables.

## AI Teacher

When enabled, the AI explanation feature can generate:

- contextual summaries in French,
- grammar breakdowns,
- vocabulary nuances,
- cultural notes,
- study tips.

The generated explanation uses the NLP analysis already produced by the application: tokenization, detected grammar patterns, extracted vocabulary and JLPT information.

## Anki export

Vocabulary can be selected and exported to a chosen Anki deck/model through AnkiConnect.

See `ANKI_SETUP.md` for configuration details.

## Project structure

```text
anime-quote-analyzer/
├── app/
│   ├── api/parse/
│   ├── api/analyze/
│   ├── api/explain/
│   └── page.tsx
├── backend/
│   ├── server.py
│   ├── analyzer.py
│   ├── jlpt_classifier.py
│   ├── grammar_detector.py
│   ├── translator.py
│   ├── ai_explainer.py
│   └── data/
├── components/
└── lib/
```

## Run locally

### Prerequisites

- Node.js 18+
- Python 3.9+
- npm

### Frontend

```bash
npm install
npm run dev
```

Frontend: `http://localhost:3000`

### Backend

```bash
cd backend
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

Then:

```bash
pip install -r requirements.txt
python server.py
```

Backend: `http://localhost:8000`

Both services are required for the full NLP workflow.

## Status

Implemented:
- subtitle parsing,
- MeCab / fugashi NLP,
- JLPT classification,
- grammar detection,
- vocabulary extraction,
- optional AI explanations,
- Anki export.

Planned:
- `.vtt` support,
- authentication,
- learning progress tracking,
- audio playback,
- testing and performance work.

## License

MIT
