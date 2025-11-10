import { NextRequest, NextResponse } from "next/server";
import { type AnalyzeResponse, type SentenceAnalysis } from "@/lib/types";

/**
 * Mock analysis function
 * TODO: Replace with actual Python NLP processing (MeCab/fugashi)
 * This is a placeholder that demonstrates the expected API response format
 */
function mockAnalyze(text: string): SentenceAnalysis {
  // Simple heuristic for demo purposes
  // In production, this would call Python backend with MeCab/fugashi
  const length = text.length;

  // Determine JLPT level based on simple heuristics (mock data)
  let jlptLevel: "N5" | "N4" | "N3" | "N2" | "N1" = "N5";
  if (length > 30) jlptLevel = "N1";
  else if (length > 20) jlptLevel = "N2";
  else if (length > 15) jlptLevel = "N3";
  else if (length > 10) jlptLevel = "N4";

  // Mock tokenization (in production, MeCab would do this)
  const mockTokens = [
    {
      surface: text.substring(0, Math.min(3, text.length)),
      reading: "もっく",
      partOfSpeech: "Noun",
      baseForm: text.substring(0, Math.min(3, text.length)),
    },
  ];

  // Mock grammar patterns
  const mockPatterns = [
    {
      pattern: "～ています",
      description: "Present progressive/continuous form",
      jlptLevel: "N5" as const,
      example: "食べています (I am eating)",
    },
  ];

  // Mock vocabulary
  const mockVocabulary = [
    {
      word: text.substring(0, Math.min(2, text.length)),
      reading: "もっく",
      meaning: "Mock translation (Python backend needed for real analysis)",
      jlptLevel: jlptLevel,
    },
  ];

  return {
    originalText: text,
    tokens: mockTokens,
    jlptLevel,
    grammarPatterns: mockPatterns,
    vocabulary: mockVocabulary,
  };
}

/**
 * API Route: POST /api/analyze
 * Accepts Japanese text and returns JLPT level + grammar analysis
 *
 * Request body:
 * {
 *   "text": "Japanese sentence here"
 * }
 *
 * Response:
 * {
 *   "success": true,
 *   "analysis": { ... }
 * }
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { text } = body;

    if (!text || typeof text !== "string") {
      return NextResponse.json(
        {
          success: false,
          analysis: null,
          error: "Invalid or missing text parameter",
        } as AnalyzeResponse & { analysis: null },
        { status: 400 }
      );
    }

    // TODO: Call Python backend for actual NLP processing
    // For now, using mock data to demonstrate the structure
    const analysis = mockAnalyze(text);

    return NextResponse.json(
      {
        success: true,
        analysis,
      } as AnalyzeResponse,
      { status: 200 }
    );
  } catch (error) {
    console.error("Analysis error:", error);
    return NextResponse.json(
      {
        success: false,
        analysis: null,
        error: "Failed to analyze text",
      } as AnalyzeResponse & { analysis: null },
      { status: 500 }
    );
  }
}
