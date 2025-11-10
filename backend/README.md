# Anime Quote Analyzer - Backend API

Japanese text analysis API using MeCab/fugashi for morphological analysis and JLPT level classification.

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- 1GB free disk space (for UniDic dictionary)

## 🚀 Installation

### 1. Navigate to backend directory

```bash
cd backend
```

### 2. Create virtual environment (recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download UniDic dictionary

The MeCab tokenizer requires a dictionary. We use `unidic-lite` (included in requirements.txt) for lightweight setup.

For better accuracy, you can optionally install the full UniDic:

```bash
python -m unidic download
```

**Note:** Full UniDic is ~800MB. `unidic-lite` (~50MB) is sufficient for most cases.

## 🏃 Running the Server

### Development mode (with auto-reload)

```bash
python server.py
```

Or using uvicorn directly:

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

### Production mode

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📡 API Documentation

Once the server is running, visit:

- **Interactive API docs:** http://localhost:8000/docs
- **Alternative docs:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health

## 🔌 API Endpoints

### POST /analyze

Analyze Japanese text and return linguistic breakdown.

**Request:**

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"私は日本語を勉強しています"}'
```

**Response:**

```json
{
  "originalText": "私は日本語を勉強しています",
  "tokens": [
    {
      "surface": "私",
      "reading": "わたし",
      "partOfSpeech": "代名詞",
      "baseForm": "私"
    },
    {
      "surface": "は",
      "reading": "は",
      "partOfSpeech": "助詞",
      "baseForm": "は"
    },
    {
      "surface": "日本語",
      "reading": "にほんご",
      "partOfSpeech": "名詞",
      "baseForm": "日本語"
    },
    {
      "surface": "を",
      "reading": "を",
      "partOfSpeech": "助詞",
      "baseForm": "を"
    },
    {
      "surface": "勉強",
      "reading": "べんきょう",
      "partOfSpeech": "名詞",
      "baseForm": "勉強"
    },
    {
      "surface": "し",
      "reading": "し",
      "partOfSpeech": "動詞",
      "baseForm": "する"
    },
    {
      "surface": "て",
      "reading": "て",
      "partOfSpeech": "助詞",
      "baseForm": "て"
    },
    {
      "surface": "い",
      "reading": "い",
      "partOfSpeech": "動詞",
      "baseForm": "いる"
    },
    {
      "surface": "ます",
      "reading": "ます",
      "partOfSpeech": "助動詞",
      "baseForm": "ます"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "～ています",
      "description": "Forme progressive/continue. Utilisée pour les actions en cours ou les états.",
      "jlptLevel": "N5",
      "example": "勉強しています (étudier)"
    }
  ],
  "vocabulary": [
    {
      "word": "私",
      "reading": "わたし",
      "meaning": "Vocab demo - Traduction nécessaire",
      "jlptLevel": "N5"
    },
    {
      "word": "日本語",
      "reading": "にほんご",
      "meaning": "Vocab demo - Traduction nécessaire",
      "jlptLevel": "N5"
    },
    {
      "word": "勉強",
      "reading": "べんきょう",
      "meaning": "Vocab demo - Traduction nécessaire",
      "jlptLevel": "N5"
    }
  ],
  "jlptLevel": "N5"
}
```

### GET /health

Health check endpoint.

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "healthy",
  "service": "anime-quote-analyzer-api"
}
```

## 🧪 Testing

### Test individual modules

```bash
# Test analyzer
python analyzer.py

# Test JLPT classifier
python jlpt_classifier.py

# Test grammar detector
python grammar_detector.py
```

### Test API endpoint

```bash
# Basic test
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"今日は良い天気です"}'

# Test with anime quote
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"君の名は？"}'
```

## 📁 Project Structure

```
backend/
├── server.py              # FastAPI server with CORS
├── analyzer.py            # Main analysis orchestrator (MeCab integration)
├── jlpt_classifier.py     # JLPT level classification
├── grammar_detector.py    # Grammar pattern detection
├── requirements.txt       # Python dependencies
├── data/
│   ├── jlpt_vocab.json    # JLPT vocabulary lists (N5-N1)
│   └── grammar_patterns.json  # Grammar pattern definitions
└── README.md             # This file
```

## 🔧 Configuration

### CORS Settings

The server is configured to accept requests from:

- `http://localhost:3000` (Next.js dev server)
- `http://127.0.0.1:3000`
- `http://localhost:3001` (alternative port)

To add more origins, edit `server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-production-domain.com",  # Add your domain
    ],
    ...
)
```

### Port Configuration

Default port is 8000. To change:

```bash
uvicorn server:app --port 8080
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'fugashi'"

**Solution:** Make sure you've activated your virtual environment and installed dependencies:

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### "Dictionary not found" error

**Solution:** Download the UniDic dictionary:

```bash
pip install unidic-lite
# or for full dictionary:
python -m unidic download
```

### CORS errors in browser

**Solution:** Make sure:

1. Backend server is running on port 8000
2. Frontend is running on port 3000
3. Both servers are started

### "Text must contain Japanese characters" error

**Solution:** Ensure your request contains actual Japanese text (hiragana, katakana, or kanji).

### Import errors when testing modules

**Solution:** Make sure you're in the `backend/` directory when running test commands:

```bash
cd backend
python analyzer.py
```

## 📚 How It Works

### 1. Tokenization (analyzer.py)

Uses **MeCab** (via fugashi) to segment Japanese text into morphemes:

- Identifies word boundaries (no spaces in Japanese!)
- Extracts part-of-speech tags
- Provides readings (pronunciation)
- Returns base forms (dictionary forms)

Example: "食べています" → ["食べ" (verb), "て" (particle), "い" (verb), "ます" (auxiliary)]

### 2. JLPT Classification (jlpt_classifier.py)

Classifies words and sentences by JLPT level:

- Maintains vocabulary lists for N5-N1
- N5 = beginner (私, 日本語, 勉強)
- N1 = advanced (哲学, 形而上学, 認識論)
- Sentence level based on word difficulty and length

### 3. Grammar Pattern Detection (grammar_detector.py)

Detects common Japanese grammar patterns:

- ～ています (progressive)
- ～ます (polite present)
- ～です (copula)
- ～たい (desire)
- And 15+ more patterns

Returns French explanations for language learners.

### 4. Vocabulary Extraction (analyzer.py)

Filters content words from tokens:

- Extracts nouns, verbs, adjectives
- Skips particles and auxiliaries
- Returns top 10 most important words
- Includes JLPT levels for study prioritization

## 🔮 Future Improvements

- [ ] Add dictionary lookup for word meanings (currently placeholder)
- [ ] Implement word frequency scoring
- [ ] Add kanji breakdown and stroke order
- [ ] Support for colloquial/slang detection
- [ ] Caching for faster repeated queries
- [ ] Database integration for user learning history
- [ ] More comprehensive grammar pattern detection
- [ ] Support for multiple dictionaries (JMDict, KANJIDIC)

## 📝 Development Notes

This backend was built to integrate with the Next.js frontend for the Anime Quote Analyzer project.

Key design decisions:

- **FastAPI** for modern, async Python web framework
- **fugashi** (MeCab wrapper) for accurate Japanese tokenization
- **unidic-lite** for lightweight deployment (vs full UniDic)
- **French descriptions** for target audience (bilingual FR/EN learners)
- **Type hints** throughout for better IDE support and documentation

## 📄 License

This project is part of the Anime Quote Analyzer portfolio project.

## 👤 Author

Maxime - Building tools for Japanese language learners
