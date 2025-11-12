# Anime Quote Analyzer

A web app for analyzing Japanese text in anime subtitles. Built to help with my own Japanese learning and as a portfolio project for summer internship applications.

⚠️ **Work in progress** - The Python NLP backend integration is coming soon. Currently using mock data for the demo.

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
- Basic UI with drag & drop upload
- Mock analysis data to demonstrate the concept
- Responsive design

**What's next:**
- Integrate Python backend with MeCab for real Japanese tokenization
- Implement actual JLPT level detection using vocabulary databases
- Grammar pattern matching
- Anki flashcard export
- User accounts and progress tracking with Supabase

## Tech Stack

**Frontend:**
- Next.js 14 (App Router) + TypeScript
- Tailwind CSS + shadcn/ui for components
- Framer Motion for animations
- Lucide React icons

**Backend (planned):**
- Python with MeCab/fugashi for Japanese NLP
- Supabase for database

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
│   ├── api/analyze/       # Text analysis (currently mock)
│   └── page.tsx           # Landing page
├── components/            # React components
│   ├── FileUploader.tsx   # Drag & drop upload
│   ├── SentenceCard.tsx   # Analysis display
│   └── JLPTBadge.tsx      # Level indicators
├── lib/                   # Utils and types
└── python/                # NLP processing (stub)
```

## Getting Started

Install dependencies:
```bash
npm install
```

Run the dev server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Development Notes

The current implementation uses mock data to demonstrate the UI and parsing logic. The actual Japanese NLP analysis will be handled by a Python backend using MeCab/fugashi, which I'm working on integrating next.

For the Python backend (when ready):
```bash
cd python
pip install -r requirements.txt
```

## Roadmap

**Phase 1: Foundation** ✅
- [x] Next.js setup
- [x] Subtitle parsing
- [x] UI components
- [x] Landing page

**Phase 2: NLP Integration** (current)
- [ ] Python backend with MeCab
- [ ] Real JLPT level detection
- [ ] Grammar pattern recognition
- [ ] Vocabulary database

**Phase 3: Features**
- [ ] Anki export (.apkg)
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

*This is a personal learning project and portfolio piece. The JLPT level detection and grammar analysis features are still in development.*
