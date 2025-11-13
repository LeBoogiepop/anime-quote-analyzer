import { NextRequest, NextResponse } from "next/server";
import { backendConfig } from "@/lib/config";
import { callBackend, BackendTimeoutError, BackendConnectionError } from "@/lib/backend-client";

/**
 * API Route: POST /api/explain
 * Generates AI-powered pedagogical explanation for a Japanese sentence
 *
 * Request body:
 * {
 *   "sentence": "Japanese sentence",
 *   "tokens": [...],
 *   "grammarPatterns": [...],
 *   "vocabulary": [...]
 * }
 *
 * Response:
 * {
 *   "success": true,
 *   "aiExplanation": {
 *     "summary": "...",
 *     "grammarNotes": [...],
 *     "vocabNotes": [...],
 *     "culturalContext": "...",
 *     "studyTips": "...",
 *     "registerNote": "..."
 *   }
 * }
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { sentence, tokens, grammarPatterns, vocabulary } = body;

    if (!sentence || typeof sentence !== "string") {
      return NextResponse.json(
        {
          success: false,
          aiExplanation: null,
          error: "Invalid or missing sentence parameter",
        },
        { status: 400 }
      );
    }

    console.log('Generating AI explanation for:', sentence.substring(0, 50));

    // Call Python backend for AI explanation
    try {
      const result = await callBackend(
        '/explain',
        'POST',
        {
          sentence,
          tokens,
          grammarPatterns,
          vocabulary
        },
        {
          timeout: backendConfig.aiExplanationTimeout,
          timeoutMessage: 'AI explanation request timed out. The AI service may be slow. Please try again.',
          connectionErrorMessage: 'Python backend is not running. Start it with: cd backend && python server.py',
        }
      );

      return NextResponse.json(
        {
          success: true,
          aiExplanation: result,
        },
        { status: 200 }
      );
    } catch (error: unknown) {
      // Handle specific backend errors
      if (error instanceof BackendTimeoutError) {
        return NextResponse.json(
          {
            success: false,
            aiExplanation: null,
            error: error.message,
          },
          { status: 504 }
        );
      }

      if (error instanceof BackendConnectionError) {
        return NextResponse.json(
          {
            success: false,
            aiExplanation: null,
            error: error.message,
          },
          { status: 503 }
        );
      }

      // Handle AI service unavailable (503 from backend)
      if (error instanceof Error && (error as Error & { status?: number }).status === 503) {
        return NextResponse.json(
          {
            success: false,
            aiExplanation: null,
            error: "AI explanation service is not configured. Please set AI_PROVIDER and API keys in backend/.env",
          },
          { status: 503 }
        );
      }

      // Re-throw other errors to be caught by outer catch
      throw error;
    }

  } catch (error) {
    console.error("AI explanation error:", error);
    return NextResponse.json(
      {
        success: false,
        aiExplanation: null,
        error: "Failed to generate AI explanation",
      },
      { status: 500 }
    );
  }
}
