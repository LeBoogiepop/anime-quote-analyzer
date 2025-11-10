import { NextRequest, NextResponse } from "next/server";

/**
 * API Route: POST /api/translate
 * Translates Japanese sentences to French using the Python backend
 *
 * Request body:
 * {
 *   "text": "Japanese sentence here"
 * }
 *
 * Response:
 * {
 *   "success": true,
 *   "originalText": "...",
 *   "translation": "..."
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
          originalText: "",
          translation: "",
          error: "Invalid or missing text parameter",
        },
        { status: 400 }
      );
    }

    console.log('Translating text:', text.substring(0, 50));

    // Call Python backend for translation
    const backendUrl = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';
    console.log('Calling Python backend at:', backendUrl);

    const startTime = Date.now();

    try {
      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      const response = await fetch(`${backendUrl}/translate-sentence`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      const duration = Date.now() - startTime;

      console.log(`✓ Translation complete in ${duration}ms`);

      return NextResponse.json(
        {
          success: true,
          originalText: result.originalText,
          translation: result.translation,
        },
        { status: 200 }
      );

    } catch (fetchError: unknown) {
      // Handle backend connection errors
      const error = fetchError as Error & { name?: string; code?: string };

      if (error.name === 'AbortError') {
        console.error('Backend request timed out after 10 seconds');
        return NextResponse.json(
          {
            success: false,
            originalText: text,
            translation: "",
            error: "Translation request timed out. The Python backend may be overloaded.",
          },
          { status: 504 }
        );
      }

      if (error.message?.includes('fetch failed') || error.code === 'ECONNREFUSED') {
        console.error('Python backend is not running');
        return NextResponse.json(
          {
            success: false,
            originalText: text,
            translation: "",
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
    console.error("Translation error:", error);
    return NextResponse.json(
      {
        success: false,
        originalText: "",
        translation: "",
        error: "Failed to translate text",
      },
      { status: 500 }
    );
  }
}
