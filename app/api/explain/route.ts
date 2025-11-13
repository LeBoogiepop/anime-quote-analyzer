import { NextRequest, NextResponse } from "next/server";

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
    const backendUrl = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';
    console.log('Calling Python backend at:', backendUrl);

    const startTime = Date.now();

    try {
      // Create abort controller for timeout (15s for AI generation)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

      const response = await fetch(`${backendUrl}/explain`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sentence,
          tokens,
          grammarPatterns,
          vocabulary
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        if (response.status === 503) {
          // AI service unavailable (not configured)
          return NextResponse.json(
            {
              success: false,
              aiExplanation: null,
              error: "AI explanation service is not configured. Please set GEMINI_API_KEY in backend/.env",
            },
            { status: 503 }
          );
        }

        throw new Error(`Backend returned ${response.status}: ${errorData.detail || response.statusText}`);
      }

      const result = await response.json();
      const duration = Date.now() - startTime;

      console.log(`✓ AI explanation generated in ${duration}ms`);

      return NextResponse.json(
        {
          success: true,
          aiExplanation: result,
        },
        { status: 200 }
      );

    } catch (fetchError: unknown) {
      // Handle backend connection errors
      const error = fetchError as Error & { name?: string; code?: string };

      if (error.name === 'AbortError') {
        console.error('Backend request timed out after 15 seconds');
        return NextResponse.json(
          {
            success: false,
            aiExplanation: null,
            error: "AI explanation request timed out. The AI service may be slow. Please try again.",
          },
          { status: 504 }
        );
      }

      if (error.message?.includes('fetch failed') || error.code === 'ECONNREFUSED') {
        console.error('Python backend is not running');
        return NextResponse.json(
          {
            success: false,
            aiExplanation: null,
            error: "Python backend is not running. Start it with: cd backend && python server.py",
          },
          { status: 503 }
        );
      }

      // Other backend errors
      console.error('Backend error:', error.message || 'Unknown error');
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
