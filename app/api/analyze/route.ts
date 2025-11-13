import { NextRequest, NextResponse } from "next/server";
import { type AnalyzeResponse } from "@/lib/types";
import { backendConfig } from "@/lib/config";
import { callBackend, BackendTimeoutError, BackendConnectionError } from "@/lib/backend-client";

/**
 * NOTE: This API route now calls the Python backend for real NLP analysis using MeCab.
 * The previous mockAnalyze() function has been removed in favor of real Japanese tokenization.
 *
 * To run the backend: cd backend && python server.py
 * Backend API documentation: http://localhost:8000/docs
 */

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

    console.log('Analyzing text:', text.substring(0, 50));

    // Call Python backend for real NLP processing
    try {
      const analysis = await callBackend<AnalyzeResponse['analysis']>(
        '/analyze',
        'POST',
        { text },
        {
          timeout: backendConfig.defaultTimeout,
          timeoutMessage: 'Backend request timed out. The Python backend may be overloaded.',
          connectionErrorMessage: 'Python backend is not running. Start it with: cd backend && python server.py',
        }
      );

      // Log detailed analysis results
      console.log(
        `✓ Analysis complete. Tokens: ${analysis.tokens?.length || 0}, ` +
        `Vocab: ${analysis.vocabulary?.length || 0}, Level: ${analysis.jlptLevel}`
      );

      return NextResponse.json(
        {
          success: true,
          analysis,
        } as AnalyzeResponse,
        { status: 200 }
      );
    } catch (error: unknown) {
      // Handle specific backend errors
      if (error instanceof BackendTimeoutError) {
        return NextResponse.json(
          {
            success: false,
            analysis: null,
            error: error.message,
          } as AnalyzeResponse & { analysis: null },
          { status: 504 }
        );
      }

      if (error instanceof BackendConnectionError) {
        return NextResponse.json(
          {
            success: false,
            analysis: null,
            error: error.message,
          } as AnalyzeResponse & { analysis: null },
          { status: 503 }
        );
      }

      // Re-throw other errors to be caught by outer catch
      throw error;
    }

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
