/**
 * JLPT (Japanese Language Proficiency Test) levels
 * N5: Beginner, N1: Advanced
 */
export type JLPTLevel = "N5" | "N4" | "N3" | "N2" | "N1";

/**
 * Represents a parsed subtitle entry
 */
export interface SubtitleEntry {
  id: number;
  startTime: string;
  endTime: string;
  text: string;
}

/**
 * Represents a Japanese word token with analysis
 */
export interface WordToken {
  surface: string; // Original form
  reading: string; // Hiragana/Katakana reading
  partOfSpeech: string; // Noun, Verb, Adjective, etc.
  baseForm: string; // Dictionary form
}

/**
 * Grammar pattern detected in a sentence
 */
export interface GrammarPattern {
  pattern: string; // e.g., "てform + います"
  description: string; // Explaination of the pattern
  jlptLevel: JLPTLevel;
  example?: string;
}

/**
 * Analysis result for a Japanese sentence
 */
export interface SentenceAnalysis {
  originalText: string;
  tokens: WordToken[];
  jlptLevel: JLPTLevel;
  grammarPatterns: GrammarPattern[];
  vocabulary: {
    word: string;
    baseForm: string; // Dictionary form for WaniKani links
    reading: string;
    meaning: string;
    jlptLevel: JLPTLevel;
  }[];
  explanation: string; // Auto-generated explanation with translation and key points
}

/**
 * Anki flashcard export format
 */
export interface AnkiCard {
  front: string; // Japanese sentence
  back: string; // Translation/Explanation
  reading: string;
  grammarNotes: string;
  tags: string[]; // JLPT level, grammar patterns, etc.
}

/**
 * API response types
 */
export interface ParseResponse {
  success: boolean;
  entries: SubtitleEntry[];
  error?: string;
}

export interface AnalyzeResponse {
  success: boolean;
  analysis: SentenceAnalysis;
  error?: string;
}
