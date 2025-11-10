import { NextRequest, NextResponse } from "next/server";
import { type AnalyzeResponse } from "@/lib/types";

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
    const backendUrl = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';
    console.log('Calling Python backend at:', backendUrl);

    const startTime = Date.now();

    try {
      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      const response = await fetch(`${backendUrl}/analyze`, {
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

      const analysis = await response.json();
      const duration = Date.now() - startTime;

      console.log(`✓ Analysis complete in ${duration}ms. Tokens: ${analysis.tokens?.length || 0}, Vocab: ${analysis.vocabulary?.length || 0}, Level: ${analysis.jlptLevel}`);

      return NextResponse.json(
        {
          success: true,
          analysis,
        } as AnalyzeResponse,
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
            analysis: null,
            error: "Backend request timed out. The Python backend may be overloaded.",
          } as AnalyzeResponse & { analysis: null },
          { status: 504 }
        );
      }

      if (error.message?.includes('fetch failed') || error.code === 'ECONNREFUSED') {
        console.error('Python backend is not running');
        return NextResponse.json(
          {
            success: false,
            analysis: null,
            error: "Python backend is not running. Start it with: cd backend && python server.py",
          } as AnalyzeResponse & { analysis: null },
          { status: 503 }
        );
      }

      // Other backend errors
      console.error('Backend error:', error.message || 'Unknown error');
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
