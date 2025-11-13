import { NextRequest, NextResponse } from "next/server";
import { type SentenceAnalysis } from "@/lib/types";

/**
 * API Route: POST /api/anki/export
 * 
 * Exports a sentence analysis to Anki using AnkiConnect.
 * 
 * AnkiConnect must be installed and running in Anki (addon code: 2055492159)
 * AnkiConnect API runs on http://localhost:8765
 * 
 * Request body:
 * {
 *   "analysis": SentenceAnalysis,
 *   "deckName": "Japanese::Anime Quotes" (optional, defaults to "Japanese::Anime Quotes"),
 *   "modelName": "Japanese Sentence" (optional, defaults to "Japanese Sentence")
 * }
 * 
 * Response:
 * {
 *   "success": true,
 *   "noteId": 1234567890,
 *   "message": "Card added successfully"
 * }
 */

const ANKICONNECT_URL = "http://localhost:8765";
const DEFAULT_DECK = "Japanese::Anime Quotes";
const DEFAULT_MODEL = "Japanese Sentence";

interface AnkiConnectRequest {
  action: string;
  version: number;
  params?: any;
}

interface AnkiConnectResponse {
  result: any;
  error: string | null;
}

/**
 * Call AnkiConnect API
 */
async function callAnkiConnect(request: AnkiConnectRequest): Promise<AnkiConnectResponse> {
  try {
    const response = await fetch(ANKICONNECT_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`AnkiConnect returned ${response.status}: ${response.statusText}`);
    }

    const data = await response.json() as AnkiConnectResponse;
    return data;
  } catch (error) {
    // Check if it's a connection error
    if (error instanceof TypeError && error.message.includes("fetch failed")) {
      throw new Error("AnkiConnect is not running. Please make sure Anki is open and AnkiConnect addon is installed.");
    }
    throw error;
  }
}

/**
 * Check if AnkiConnect is available
 */
async function checkAnkiConnect(): Promise<boolean> {
  try {
    const response = await callAnkiConnect({
      action: "version",
      version: 6,
    });
    return response.error === null;
  } catch (error) {
    return false;
  }
}

/**
 * Ensure deck exists, create if not
 */
async function ensureDeck(deckName: string): Promise<void> {
  const response = await callAnkiConnect({
    action: "deckNames",
    version: 6,
  });

  if (response.error) {
    throw new Error(`Failed to get deck names: ${response.error}`);
  }

  const decks = response.result as string[];
  if (!decks.includes(deckName)) {
    // Create deck
    const createResponse = await callAnkiConnect({
      action: "createDeck",
      version: 6,
      params: {
        deck: deckName,
      },
    });

    if (createResponse.error) {
      throw new Error(`Failed to create deck: ${createResponse.error}`);
    }
  }
}

/**
 * Ensure note type (model) exists, create if not
 */
async function ensureModel(modelName: string): Promise<void> {
  const response = await callAnkiConnect({
    action: "modelNames",
    version: 6,
  });

  if (response.error) {
    throw new Error(`Failed to get model names: ${response.error}`);
  }

  const models = response.result as string[];
  if (!models.includes(modelName)) {
    // Create model with fields: Japanese, Reading, Translation, Grammar, Vocabulary, JLPT, Tags
    const createResponse = await callAnkiConnect({
      action: "createModel",
      version: 6,
      params: {
        modelName: modelName,
        inOrderFields: [
          "Japanese",
          "Reading",
          "Translation",
          "Grammar",
          "Vocabulary",
          "JLPT",
          "Tags",
        ],
        css: `
.card {
  font-family: "Noto Sans JP", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
  font-size: 18px;
  text-align: center;
  color: #2c3e50;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 10px;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.jp {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 12px;
  color: #fff;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
}

.reading {
  font-size: 16px;
  color: rgba(255,255,255,0.9);
  margin-bottom: 20px;
  line-height: 1.6;
}

.translation {
  font-size: 16px;
  color: rgba(255,255,255,0.95);
  margin-bottom: 15px;
  font-style: italic;
  background: rgba(255,255,255,0.1);
  padding: 10px;
  border-radius: 5px;
}

.grammar, .vocab {
  font-size: 13px;
  text-align: left;
  margin-top: 12px;
  padding: 12px;
  background: rgba(255,255,255,0.15);
  border-radius: 6px;
  color: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  line-height: 1.5;
}

.jlpt {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
  margin-top: 12px;
  background: rgba(255,255,255,0.2);
  color: #fff;
}
        `,
        cardTemplates: [
          {
            Name: "Card 1",
            Front: `
<div class="jp">{{Japanese}}</div>
<div class="reading">{{Reading}}</div>
            `,
            Back: `
<div class="jp">{{Japanese}}</div>
<div class="reading">{{Reading}}</div>
<hr>
<div class="translation">{{Translation}}</div>
<div class="grammar">{{Grammar}}</div>
<div class="vocab">{{Vocabulary}}</div>
<div class="jlpt">{{JLPT}}</div>
            `,
          },
        ],
      },
    });

    if (createResponse.error) {
      throw new Error(`Failed to create model: ${createResponse.error}`);
    }
  }
}

/**
 * Format analysis data for Anki card
 */
function formatAnkiCard(
  analysis: SentenceAnalysis,
  config: {
    selectedVocab: string[];
    includeGrammar: boolean;
    includeTranslation: boolean;
  }
): {
  Japanese: string;
  Reading: string;
  Translation: string;
  Grammar: string;
  Vocabulary: string;
  JLPT: string;
  Tags: string;
} {
  // Format reading (furigana) - combine all token readings
  const reading = analysis.tokens
    .map((token) => {
      const surface = token.surface;
      const reading = token.reading;
      // Only show reading if different from surface and contains kanji
      if (reading && reading !== surface && /[\u4E00-\u9FAF]/.test(surface)) {
        return `${surface}[${reading}]`;
      }
      return surface;
    })
    .join(" ");

  // Format grammar patterns (only if enabled)
  const grammar = config.includeGrammar
    ? analysis.grammarPatterns
        .map((pattern) => `• ${pattern.pattern}: ${pattern.description}`)
        .join("\n") || ""
    : "";

  // Format vocabulary (only selected words)
  const vocabulary = config.selectedVocab.length > 0
    ? analysis.vocabulary
        .filter((vocab) => config.selectedVocab.includes(vocab.word))
        .map((vocab) => `• ${vocab.word} (${vocab.reading}): ${vocab.meaning}`)
        .join("\n")
    : "";

  // Format tags: JLPT level + grammar patterns + selected vocab
  const tags = [
    analysis.jlptLevel,
    ...analysis.grammarPatterns.map((p) => p.pattern),
    ...config.selectedVocab,
    "anime",
    "sentence",
  ].join(" ");

  return {
    Japanese: analysis.originalText || "",
    Reading: reading || "",
    Translation: config.includeTranslation ? "" : "",
    Grammar: grammar || "",
    Vocabulary: vocabulary || "",
    JLPT: analysis.jlptLevel || "",
    Tags: tags || "",
  };
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      analysis,
      deckName = DEFAULT_DECK,
      modelName = DEFAULT_MODEL,
      selectedVocab = analysis?.vocabulary?.map((v: any) => v.word) || [],
      includeGrammar = true,
      includeTranslation = true,
    } = body;

    if (!analysis) {
      return NextResponse.json(
        {
          success: false,
          error: "Missing analysis data",
        },
        { status: 400 }
      );
    }

    // Validate analysis structure
    if (!analysis.originalText || !analysis.tokens || !analysis.jlptLevel) {
      return NextResponse.json(
        {
          success: false,
          error: "Invalid analysis data structure",
        },
        { status: 400 }
      );
    }

    console.log(`Exporting to Anki: "${analysis.originalText.substring(0, 30)}..."`);

    // Check if AnkiConnect is available
    const isAvailable = await checkAnkiConnect();
    if (!isAvailable) {
      return NextResponse.json(
        {
          success: false,
          error: "AnkiConnect is not available. Please make sure:\n1. Anki is running\n2. AnkiConnect addon is installed (code: 2055492159)\n3. AnkiConnect is enabled",
        },
        { status: 503 }
      );
    }

    // Ensure deck and model exist
    await ensureDeck(deckName);
    await ensureModel(modelName);

    // Format card data
    const cardFields = formatAnkiCard(analysis as SentenceAnalysis, {
      selectedVocab,
      includeGrammar,
      includeTranslation,
    });

    // Validate that required fields are not empty
    if (!cardFields.Japanese || cardFields.Japanese.trim() === "") {
      return NextResponse.json(
        {
          success: false,
          error: "Japanese field cannot be empty",
        },
        { status: 400 }
      );
    }

    // Ensure at least Reading or Vocabulary has content (these are essential)
    const hasEssentialContent = 
      (cardFields.Reading && cardFields.Reading.trim() !== "") ||
      (cardFields.Vocabulary && cardFields.Vocabulary.trim() !== "");

    if (!hasEssentialContent) {
      return NextResponse.json(
        {
          success: false,
          error: "At least Reading or Vocabulary must have content. Please select at least one vocabulary word to export.",
        },
        { status: 400 }
      );
    }

    // Add note to Anki
    const addNoteResponse = await callAnkiConnect({
      action: "addNote",
      version: 6,
      params: {
        note: {
          deckName: deckName,
          modelName: modelName,
          fields: cardFields,
          tags: cardFields.Tags ? cardFields.Tags.split(" ").filter((t) => t.trim() !== "") : [],
        },
      },
    });

    if (addNoteResponse.error) {
      return NextResponse.json(
        {
          success: false,
          error: `Failed to add note to Anki: ${addNoteResponse.error}`,
        },
        { status: 500 }
      );
    }

    const noteId = addNoteResponse.result;

    console.log(`✓ Card added to Anki with note ID: ${noteId}`);

    return NextResponse.json(
      {
        success: true,
        noteId: noteId,
        message: "Card added successfully to Anki",
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("Anki export error:", error);
    const errorMessage = error instanceof Error ? error.message : "Unknown error occurred";

    return NextResponse.json(
      {
        success: false,
        error: errorMessage,
      },
      { status: 500 }
    );
  }
}

