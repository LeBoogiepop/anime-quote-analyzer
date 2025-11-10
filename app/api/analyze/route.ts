import { NextRequest, NextResponse } from "next/server";
import { type AnalyzeResponse, type SentenceAnalysis } from "@/lib/types";

/**
 * Mock analysis function
 * TODO: Replace with actual Python NLP processing (MeCab/fugashi)
 * This creates realistic-looking mock data for demonstration
 */
function mockAnalyze(text: string): SentenceAnalysis {
  // Mock tokenization - detect common Japanese words and particles
  const tokens = [];

  // Mock tokenization with varied readings
  if (text.includes('私')) {
    tokens.push({ surface: '私', reading: 'わたし', partOfSpeech: 'Pronoun', baseForm: '私' });
  }
  if (text.includes('は')) {
    tokens.push({ surface: 'は', reading: 'は', partOfSpeech: 'Particle', baseForm: 'は' });
  }
  if (text.includes('日本語')) {
    tokens.push({ surface: '日本語', reading: 'にほんご', partOfSpeech: 'Noun', baseForm: '日本語' });
  }
  if (text.includes('勉強')) {
    tokens.push({ surface: '勉強', reading: 'べんきょう', partOfSpeech: 'Noun', baseForm: '勉強' });
  }
  if (text.includes('して')) {
    tokens.push({ surface: 'して', reading: 'して', partOfSpeech: 'Verb', baseForm: 'する' });
  }
  if (text.includes('います')) {
    tokens.push({ surface: 'います', reading: 'います', partOfSpeech: 'Verb', baseForm: 'いる' });
  }
  if (text.includes('を')) {
    tokens.push({ surface: 'を', reading: 'を', partOfSpeech: 'Particle', baseForm: 'を' });
  }
  if (text.includes('が')) {
    tokens.push({ surface: 'が', reading: 'が', partOfSpeech: 'Particle', baseForm: 'が' });
  }
  if (text.includes('です')) {
    tokens.push({ surface: 'です', reading: 'です', partOfSpeech: 'Auxiliary', baseForm: 'です' });
  }
  if (text.includes('ます')) {
    tokens.push({ surface: 'ます', reading: 'ます', partOfSpeech: 'Auxiliary', baseForm: 'ます' });
  }
  if (text.includes('今日')) {
    tokens.push({ surface: '今日', reading: 'きょう', partOfSpeech: 'Noun', baseForm: '今日' });
  }
  if (text.includes('天気')) {
    tokens.push({ surface: '天気', reading: 'てんき', partOfSpeech: 'Noun', baseForm: '天気' });
  }
  if (text.includes('大学')) {
    tokens.push({ surface: '大学', reading: 'だいがく', partOfSpeech: 'Noun', baseForm: '大学' });
  }
  if (text.includes('毎日')) {
    tokens.push({ surface: '毎日', reading: 'まいにち', partOfSpeech: 'Noun', baseForm: '毎日' });
  }

  // Determine JLPT level based on length and complexity
  const length = text.length;
  const hasKanji = /[\u4e00-\u9faf]/.test(text);
  let jlptLevel: "N5" | "N4" | "N3" | "N2" | "N1" = "N5";

  if (length > 25 && hasKanji) jlptLevel = "N2";
  else if (length > 20) jlptLevel = "N3";
  else if (length > 12) jlptLevel = "N4";

  // Detect grammar patterns based on sentence content
  const grammarPatterns = [];

  if (text.includes('ています')) {
    grammarPatterns.push({
      pattern: '～ています',
      description: 'Forme progressive/continue. Utilisée pour les actions en cours ou les états.',
      jlptLevel: 'N5' as const,
      example: '勉強しています (étudier)'
    });
  }
  if (text.includes('ます')) {
    grammarPatterns.push({
      pattern: '～ます',
      description: 'Forme polie présent/futur des verbes.',
      jlptLevel: 'N5' as const,
      example: '行きます (aller)'
    });
  }
  if (text.includes('です')) {
    grammarPatterns.push({
      pattern: '～です',
      description: 'Copule polie. Utilisée pour exprimer "être".',
      jlptLevel: 'N5' as const,
      example: '学生です (être étudiant)'
    });
  }
  if (text.includes('ませんか')) {
    grammarPatterns.push({
      pattern: '～ませんか',
      description: 'Forme interrogative négative. Utilisée pour faire des invitations polies.',
      jlptLevel: 'N5' as const,
      example: '行きませんか (voulez-vous aller?)'
    });
  }
  if (text.includes('でしょう')) {
    grammarPatterns.push({
      pattern: '～でしょう',
      description: 'Marqueur de probabilité/conjecture. "probablement/je pense".',
      jlptLevel: 'N4' as const,
      example: '雨でしょう (probablement de la pluie)'
    });
  }

  // Generate vocabulary entries
  const vocabulary = [];

  if (text.includes('私')) {
    vocabulary.push({ word: '私', reading: 'わたし', meaning: 'I, me', jlptLevel: 'N5' as const });
  }
  if (text.includes('日本語')) {
    vocabulary.push({ word: '日本語', reading: 'にほんご', meaning: 'Japanese language', jlptLevel: 'N5' as const });
  }
  if (text.includes('勉強')) {
    vocabulary.push({ word: '勉強する', reading: 'べんきょうする', meaning: 'to study', jlptLevel: 'N5' as const });
  }
  if (text.includes('今日')) {
    vocabulary.push({ word: '今日', reading: 'きょう', meaning: 'today', jlptLevel: 'N5' as const });
  }
  if (text.includes('天気')) {
    vocabulary.push({ word: '天気', reading: 'てんき', meaning: 'weather', jlptLevel: 'N5' as const });
  }
  if (text.includes('大学')) {
    vocabulary.push({ word: '大学', reading: 'だいがく', meaning: 'university', jlptLevel: 'N5' as const });
  }
  if (text.includes('毎日')) {
    vocabulary.push({ word: '毎日', reading: 'まいにち', meaning: 'every day', jlptLevel: 'N5' as const });
  }
  if (text.includes('図書館')) {
    vocabulary.push({ word: '図書館', reading: 'としょかん', meaning: 'library', jlptLevel: 'N4' as const });
  }
  if (text.includes('頑張')) {
    vocabulary.push({ word: '頑張る', reading: 'がんばる', meaning: 'to do one\'s best', jlptLevel: 'N4' as const });
  }

  // If no patterns detected, add default
  if (grammarPatterns.length === 0) {
    grammarPatterns.push({
      pattern: 'Phrase simple',
      description: 'Structure de phrase déclarative simple.',
      jlptLevel: 'N5' as const,
      example: 'これは本です (Ceci est un livre)'
    });
  }

  // If no vocabulary detected, extract words (not characters or substrings)
  if (vocabulary.length === 0) {
    // Extract words using proper patterns
    const kanjiWords = text.match(/[\u4E00-\u9FAF]+[\u3040-\u309F]*/g) || [];
    const hiraganaWords = text.match(/[\u3040-\u309F]{2,}/g) || [];
    const katakanaWords = text.match(/[\u30A0-\u30FF]{2,}/g) || [];

    // Combine and deduplicate
    const allWords = Array.from(new Set([...kanjiWords, ...hiraganaWords, ...katakanaWords]));

    // Filter out particles and take first 3-4 words
    const particles = ['は', 'が', 'を', 'に', 'へ', 'で', 'と'];
    const filtered = allWords.filter(w => !particles.includes(w)).slice(0, 4);

    filtered.forEach(word => {
      const isHiragana = /^[\u3040-\u309F]+$/.test(word);
      const isKatakana = /^[\u30A0-\u30FF]+$/.test(word);

      vocabulary.push({
        word: word,
        reading: (isHiragana || isKatakana) ? word : 'demo',
        meaning: 'Démo - Backend Python NLP nécessaire pour l\'analyse complète',
        jlptLevel: jlptLevel
      });
    });
  }

  // If no tokens detected, extract word-level tokens
  if (tokens.length === 0) {
    // Extract words using proper patterns
    const kanjiWords = text.match(/[\u4E00-\u9FAF]+[\u3040-\u309F]*/g) || [];
    const hiraganaWords = text.match(/[\u3040-\u309F]{2,}/g) || [];
    const katakanaWords = text.match(/[\u30A0-\u30FF]{2,}/g) || [];
    const particles = text.match(/[はがをにへでと]/g) || [];

    // Combine all matches
    const allMatches = [...kanjiWords, ...hiraganaWords, ...katakanaWords, ...particles];

    allMatches.forEach(word => {
      const isHiragana = /^[\u3040-\u309F]+$/.test(word);
      const isKatakana = /^[\u30A0-\u30FF]+$/.test(word);
      const isParticle = /^[はがをにへでと]$/.test(word);

      tokens.push({
        surface: word,
        reading: (isHiragana || isKatakana) ? word : 'demo',
        partOfSpeech: isParticle ? 'Particle' : 'Word',
        baseForm: word
      });
    });
  }

  return {
    originalText: text,
    tokens: tokens.length > 0 ? tokens : [{ surface: text, reading: 'demo', partOfSpeech: 'Unknown', baseForm: text }],
    jlptLevel,
    grammarPatterns,
    vocabulary,
  };
}

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

    // TODO: Call Python backend for actual NLP processing
    // For now, using mock data to demonstrate the structure
    const analysis = mockAnalyze(text);

    return NextResponse.json(
      {
        success: true,
        analysis,
      } as AnalyzeResponse,
      { status: 200 }
    );
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
