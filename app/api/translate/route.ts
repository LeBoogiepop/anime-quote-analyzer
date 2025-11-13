import { NextRequest, NextResponse } from "next/server";
import { backendConfig } from "@/lib/config";
import { callBackend, BackendTimeoutError, BackendConnectionError } from "@/lib/backend-client";

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
    try {
      const result = await callBackend<{ originalText: string; translation: string }>(
        '/translate-sentence',
        'POST',
        { text },
        {
          timeout: backendConfig.translationTimeout,
          timeoutMessage: 'Translation request timed out. The translation service may be slow or overloaded.',
          connectionErrorMessage: 'Python backend is not running. Start it with: cd backend && python server.py',
        }
      );

      return NextResponse.json(
        {
          success: true,
          originalText: result.originalText,
          translation: result.translation,
        },
        { status: 200 }
      );
    } catch (error: unknown) {
      // Handle specific backend errors
      if (error instanceof BackendTimeoutError) {
        return NextResponse.json(
          {
            success: false,
            originalText: text,
            translation: "",
            error: error.message,
          },
          { status: 504 }
        );
      }

      if (error instanceof BackendConnectionError) {
        return NextResponse.json(
          {
            success: false,
            originalText: text,
            translation: "",
            error: error.message,
          },
          { status: 503 }
        );
      }

      // Re-throw other errors to be caught by outer catch
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
