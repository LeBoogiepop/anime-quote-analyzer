"""
FastAPI server for Japanese text analysis.

This server provides NLP analysis for Japanese text using MeCab/fugashi.
It's designed to work with the Next.js frontend for the Anime Quote Analyzer.

Author: Maxime
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal, Optional
import logging

from analyzer import analyze_text
from translator import translate_sentence

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Anime Quote Analyzer API",
    description="Japanese text analysis API using MeCab for tokenization and JLPT classification",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Request/Response models matching TypeScript types
class AnalyzeRequest(BaseModel):
    """Request body for text analysis."""
    text: str


class TranslateRequest(BaseModel):
    """Request body for sentence translation."""
    text: str


class TranslateResponse(BaseModel):
    """Translation response."""
    originalText: str
    translation: str


class Token(BaseModel):
    """Word token with linguistic information."""
    surface: str
    reading: str
    partOfSpeech: str
    baseForm: str


class GrammarPattern(BaseModel):
    """Detected grammar pattern."""
    pattern: str
    description: str
    jlptLevel: Literal["N5", "N4", "N3", "N2", "N1"]
    example: str
    exampleInSentence: Optional[str] = None
    pedagogicalNote: Optional[str] = None


class Vocabulary(BaseModel):
    """Vocabulary entry with JLPT level."""
    word: str
    baseForm: str  # Dictionary form for WaniKani links
    reading: str
    meaning: str
    jlptLevel: Literal["N5", "N4", "N3", "N2", "N1", "Unknown"]


class AnalyzeResponse(BaseModel):
    """Complete analysis response."""
    originalText: str
    tokens: List[Token]
    grammarPatterns: List[GrammarPattern]
    vocabulary: List[Vocabulary]
    jlptLevel: Literal["N5", "N4", "N3", "N2", "N1"]


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Anime Quote Analyzer API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "/analyze": "POST - Analyze Japanese text",
            "/translate-sentence": "POST - Translate Japanese sentence to French",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "anime-quote-analyzer-api"
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Analyze Japanese text and return linguistic breakdown.

    This endpoint:
    1. Tokenizes the text using MeCab/fugashi
    2. Extracts vocabulary with JLPT levels
    3. Detects grammar patterns
    4. Classifies overall sentence JLPT level

    Args:
        request: AnalyzeRequest containing the Japanese text

    Returns:
        AnalyzeResponse with complete linguistic analysis

    Raises:
        HTTPException: If text is empty or analysis fails
    """
    text = request.text.strip()

    # Validate input
    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )

    # Check if text contains Japanese characters
    if not any('\u3040' <= char <= '\u309F' or  # Hiragana
               '\u30A0' <= char <= '\u30FF' or  # Katakana
               '\u4E00' <= char <= '\u9FAF'     # Kanji
               for char in text):
        raise HTTPException(
            status_code=400,
            detail="Text must contain Japanese characters"
        )

    try:
        logger.info(f"Analyzing text: {text[:50]}...")

        # Perform analysis using analyzer module
        result = analyze_text(text)

        logger.info(f"Analysis complete. JLPT Level: {result['jlptLevel']}, "
                   f"Tokens: {len(result['tokens'])}, "
                   f"Vocab: {len(result['vocabulary'])}")

        return result

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/translate-sentence", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    Translate Japanese sentence to French.

    This endpoint translates full Japanese sentences to French.
    Currently returns a placeholder message indicating DeepL integration is planned.

    Args:
        request: TranslateRequest containing the Japanese text

    Returns:
        TranslateResponse with original text and French translation

    Raises:
        HTTPException: If text is empty or translation fails
    """
    text = request.text.strip()

    # Validate input
    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )

    # Check if text contains Japanese characters
    if not any('\u3040' <= char <= '\u309F' or  # Hiragana
               '\u30A0' <= char <= '\u30FF' or  # Katakana
               '\u4E00' <= char <= '\u9FAF'     # Kanji
               for char in text):
        raise HTTPException(
            status_code=400,
            detail="Text must contain Japanese characters"
        )

    try:
        logger.info(f"Translating sentence: {text[:50]}...")

        # Get translation using translator service
        translation = translate_sentence(text)

        logger.info(f"Translation complete: {translation[:50]}...")

        return {
            "originalText": text,
            "translation": translation
        }

    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Anime Quote Analyzer API...")
    print("📝 API docs available at: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
