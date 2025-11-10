import { NextRequest, NextResponse } from "next/server";
import { type SubtitleEntry, type ParseResponse } from "@/lib/types";

/**
 * Check if text contains Japanese characters (hiragana, katakana, or kanji)
 */
function hasJapaneseContent(text: string): boolean {
  // Unicode ranges: Hiragana (3040-309F), Katakana (30A0-30FF), Kanji (4E00-9FAF)
  return /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(text);
}

/**
 * Check if text only contains music symbols and common punctuation
 */
function isOnlySymbols(text: string): boolean {
  // Remove music symbols, tildes, whitespace, and common punctuation
  const cleaned = text.replace(/[♪♫♬〜～\s.,!?。、]/g, '');
  // If nothing left after removing symbols, it's only symbols
  return cleaned.length === 0;
}

/**
 * Remove speaker labels from subtitle text
 * Examples: （教師）よ〜し → よ〜し, (話し声) → empty string
 */
function removeSpeakerLabels(text: string): string {
  // Remove speaker labels at the start: （...） or (...)
  return text.replace(/^[\(（][^\)）]+[\)）]\s*/g, '').trim();
}

/**
 * Comprehensive subtitle text cleaning function.
 *
 * Cleaning steps:
 * 1. Remove speaker labels: （教師）, （タカギ）, (話し声), etc.
 * 2. Remove standalone music symbols: ♪, ♫, ♬
 * 3. Remove common subtitle formatting artifacts
 * 4. Normalize whitespace (multiple spaces/tabs → single space)
 * 5. Trim leading/trailing whitespace
 *
 * @param text - Raw subtitle text
 * @returns Cleaned text ready for analysis
 */
function cleanSubtitleText(text: string): string {
  let cleaned = text;

  // Step 1: Remove speaker labels at the start
  cleaned = removeSpeakerLabels(cleaned);

  // Step 2: Remove standalone music symbols (not part of actual dialogue)
  // Only remove if they're at start/end or surrounded by whitespace
  cleaned = cleaned.replace(/^\s*[♪♫♬]+\s*/g, '');  // Start
  cleaned = cleaned.replace(/\s*[♪♫♬]+\s*$/g, '');  // End
  cleaned = cleaned.replace(/\s+[♪♫♬]+\s+/g, ' '); // Middle (surrounded by spaces)

  // Step 3: Remove common subtitle formatting artifacts
  cleaned = cleaned.replace(/\\N/g, ' ');           // ASS line breaks
  cleaned = cleaned.replace(/\{[^}]*\}/g, '');      // ASS formatting tags
  cleaned = cleaned.replace(/<[^>]*>/g, '');        // HTML-like tags

  // Step 4: Normalize whitespace
  cleaned = cleaned.replace(/\s+/g, ' ');           // Multiple spaces → single space
  cleaned = cleaned.replace(/\t+/g, ' ');           // Tabs → space

  // Step 5: Trim and return
  return cleaned.trim();
}

/**
 * Parse SRT subtitle file format
 * Format:
 * 1
 * 00:00:01,000 --> 00:00:04,000
 * Subtitle text here
 */
function parseSRT(content: string): SubtitleEntry[] {
  const entries: SubtitleEntry[] = [];
  const blocks = content.trim().split(/\n\s*\n/);

  for (const block of blocks) {
    const lines = block.split("\n");
    if (lines.length < 3) continue;

    const id = parseInt(lines[0]);
    const timeLine = lines[1];
    let text = lines.slice(2).join("\n").trim();

    // Parse time format: 00:00:01,000 --> 00:00:04,000
    const timeMatch = timeLine.match(
      /(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})/
    );

    if (timeMatch) {
      // Clean subtitle text (remove labels, symbols, normalize whitespace)
      text = cleanSubtitleText(text);

      // Skip empty entries after cleaning
      if (!text) {
        continue;
      }

      // Skip entries that are only symbols or don't contain Japanese
      if (isOnlySymbols(text) || !hasJapaneseContent(text)) {
        console.log('Skipping non-Japanese entry:', text);
        continue;
      }

      entries.push({
        id,
        startTime: timeMatch[1],
        endTime: timeMatch[2],
        text,
      });
    }
  }

  return entries;
}

/**
 * Parse ASS/SSA subtitle file format (simplified)
 * Extracts dialogue lines from ASS format
 */
function parseASS(content: string): SubtitleEntry[] {
  const entries: SubtitleEntry[] = [];
  const lines = content.split("\n");
  let id = 1;

  for (const line of lines) {
    // Look for dialogue lines: Dialogue: 0,0:00:01.00,0:00:04.00,Default,,0,0,0,,Text here
    if (line.startsWith("Dialogue:")) {
      const parts = line.split(",");
      if (parts.length >= 10) {
        const startTime = parts[1];
        const endTime = parts[2];
        let text = parts.slice(9).join(",").replace(/\{[^}]*\}/g, "").trim();

        // Clean subtitle text (remove labels, symbols, normalize whitespace)
        text = cleanSubtitleText(text);

        // Skip empty entries after cleaning
        if (!text) {
          continue;
        }

        // Skip entries that are only symbols or don't contain Japanese
        if (isOnlySymbols(text) || !hasJapaneseContent(text)) {
          console.log('Skipping non-Japanese entry:', text);
          continue;
        }

        entries.push({
          id: id++,
          startTime,
          endTime,
          text,
        });
      }
    }
  }

  return entries;
}

/**
 * API Route: POST /api/parse
 * Accepts subtitle file and returns parsed entries
 */
export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get("file") as File;

    if (!file) {
      return NextResponse.json(
        {
          success: false,
          entries: [],
          error: "No file provided",
        } as ParseResponse,
        { status: 400 }
      );
    }

    const content = await file.text();
    const fileName = file.name.toLowerCase();
    console.log('Parsing subtitle file:', fileName, 'size:', content.length);

    let entries: SubtitleEntry[];

    // TODO maxime: add support for .vtt format
    if (fileName.endsWith(".srt")) {
      entries = parseSRT(content);
    } else if (fileName.endsWith(".ass") || fileName.endsWith(".ssa")) {
      entries = parseASS(content);
    } else {
      return NextResponse.json(
        {
          success: false,
          entries: [],
          error: "Unsupported file format. Please use .srt or .ass files.",
        } as ParseResponse,
        { status: 400 }
      );
    }

    return NextResponse.json(
      {
        success: true,
        entries,
      } as ParseResponse,
      { status: 200 }
    );
  } catch (error) {
    console.error("Parse error:", error);
    return NextResponse.json(
      {
        success: false,
        entries: [],
        error: "Failed to parse subtitle file",
      } as ParseResponse,
      { status: 500 }
    );
  }
}
