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
  description: string; // Explanation of the pattern
  jlptLevel: JLPTLevel;
  example?: string; // Generic example
  exampleInSentence?: string; // Actual example extracted from analyzed sentence
  pedagogicalNote?: string; // Practical usage advice
}

/**
 * Grammar note in AI explanation
 */
export interface GrammarNote {
  pattern: string;
  explanation: string;
  example?: string;
}

/**
 * Vocabulary note in AI explanation
 */
export interface VocabNote {
  word: string;
  reading?: string;
  nuance: string;
}

/**
 * AI-generated pedagogical explanation
 */
export interface AIExplanation {
  summary: string;
  grammarNotes: GrammarNote[];
  vocabNotes: VocabNote[];
  culturalContext?: string;
  studyTips?: string;
  registerNote?: string;
  simpleTranslation: string;
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
