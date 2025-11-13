# Anime Quote Analyzer

A web app for analyzing Japanese text in anime subtitles. Built to help with my own Japanese learning and as a portfolio project for summer internship applications.

✅ **Backend integrated** - Full Japanese NLP analysis using MeCab/fugashi is now working!

[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3-38bdf8)](https://tailwindcss.com/)

## Why I Built This

I've been learning Japanese for about a year now, mostly through watching anime. I kept finding myself pausing to look up words and grammar patterns, and thought - why not build something to automate this? Plus, I'm applying for internships in Tokyo next summer, so this project lets me showcase full-stack development skills while solving a real problem I have.

The goal is to upload anime subtitle files (.srt, .ass) and get instant breakdowns of:
- JLPT level estimates for sentences
- Grammar pattern explanations
- Vocabulary with readings and meanings
- Exportable Anki flashcards (eventually)

## Current Status

**What works:**
- Subtitle file parsing (.srt and .ass formats)
- Full Japanese NLP analysis with MeCab/fugashi tokenization
- Real JLPT level detection (N5-N1)
- Grammar pattern recognition and explanations
- Vocabulary extraction with French translations
- AI-powered explanations (optional, via OpenRouter or Gemini)
- Responsive UI with drag & drop upload

**What's next:**
- Anki flashcard export (.apkg format)
- User accounts and progress tracking
- Support for .vtt subtitle format

## Tech Stack

**Frontend:**
- Next.js 14 (App Router) + TypeScript
- Tailwind CSS + shadcn/ui for components
- Framer Motion for animations
- Lucide React icons

**Backend:**
- Python FastAPI with MeCab/fugashi for Japanese NLP
- Real-time tokenization and JLPT classification
- AI explanations via OpenRouter (Perplexity) or Google Gemini

## 🎓 AI Teacher Feature (Optional)

Get AI-powered pedagogical explanations on demand! When enabled, each sentence gets an "Explication" button that generates:
- **Contextualized summary** in natural French
- **Grammar breakdowns** with practical explanations
- **Vocabulary nuances** beyond dictionary definitions
- **Cultural context** notes when relevant
- **Study tips** and memory aids

### Setup (OpenRouter - Recommended)

1. Get a free API key from [OpenRouter](https://openrouter.ai/keys)
2. Configure in `backend/.env`:
```bash
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
AI_MODEL=perplexity/sonar-small-chat
```
3. Install dependencies: `cd backend && pip install -r requirements.txt`
4. Restart the backend server

**Why OpenRouter?**
- Free tier: ~2,000 requests/month with Perplexity Sonar
- Fast responses (2-4 seconds)
- Cost-effective for personal use
- Access to multiple AI models through one API

### Alternative Setup (Google Gemini)

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/)
2. Configure in `backend/.env`:
```bash
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
AI_MODEL=gemini-1.5-flash-latest
```

**Gemini Free Tier:** 1,500 requests/day

### Usage

- Click the "Explication" button on any analyzed sentence
- AI generates explanation in 5-10 seconds
- Results are cached for 24h to save quota
- **Privacy:** Sentences are sent to the AI provider for processing

### How It Works

The AI Teacher analyzes each sentence using:
- MeCab tokenization data
- Detected grammar patterns
- Extracted vocabulary
- JLPT level information

Then generates explanations tailored to French-speaking learners, focusing on practical usage rather than academic terminology.

## Project Structure

```
anime-quote-analyzer/
├── app/                    # Next.js pages and API routes
│   ├── api/parse/         # Subtitle parsing
│   ├── api/analyze/       # Text analysis (calls Python backend)
│   ├── api/explain/       # AI explanations
│   └── page.tsx           # Landing page
├── backend/               # Python FastAPI backend
│   ├── server.py         # FastAPI server
│   ├── analyzer.py        # MeCab tokenization & analysis
│   ├── jlpt_classifier.py # JLPT level detection
│   ├── grammar_detector.py # Grammar pattern matching
│   ├── translator.py     # Translation service
│   ├── ai_explainer.py    # AI explanation generator
│   └── data/              # Vocabulary & grammar databases
├── components/            # React components
│   ├── FileUploader.tsx   # Drag & drop upload
│   ├── SentenceCard.tsx   # Analysis display
│   └── JLPTBadge.tsx      # Level indicators
└── lib/                   # Utils and types
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- 1GB free disk space (for UniDic dictionary)

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Run the dev server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables (optional):
```bash
# Copy the example file
cp env.example .env
# Edit .env with your API keys if you want AI explanations
```

5. Start the backend server:
```bash
python server.py
```

The backend will run on `http://localhost:8000`

**Note:** Both servers need to be running for full functionality. The frontend calls the Python backend for NLP analysis.

## Roadmap

**Phase 1: Foundation** ✅
- [x] Next.js setup
- [x] Subtitle parsing (.srt, .ass)
- [x] UI components
- [x] Landing page

**Phase 2: NLP Integration** ✅
- [x] Python backend with FastAPI
- [x] MeCab/fugashi tokenization
- [x] Real JLPT level detection (N5-N1)
- [x] Grammar pattern recognition
- [x] Vocabulary extraction with translations
- [x] AI-powered explanations (optional)

**Phase 3: Features** (current)
- [ ] Anki export (.apkg format)
- [ ] Support for .vtt subtitle format
- [ ] User authentication
- [ ] Learning progress tracking
- [ ] Audio playback

**Phase 4: Polish**
- [ ] Testing
- [ ] Performance optimization
- [ ] Deployment

## License

MIT

## Contact

Feel free to open an issue if you have questions or suggestions!

---

*This is a personal learning project and portfolio piece. Built with Next.js, FastAPI, and MeCab for Japanese language learning.*
