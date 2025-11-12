"use client";

import { useState } from "react";
import { type SentenceAnalysis, type AIExplanation } from "@/lib/types";
import { JLPTBadge } from "./JLPTBadge";
import { motion, AnimatePresence } from "framer-motion";
import { BookOpen, GraduationCap, Languages, ExternalLink, Eye, EyeOff, Loader2, Sparkles } from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";

interface SentenceCardProps {
  analysis: SentenceAnalysis;
  index?: number;
}

// Displays analyzed Japanese sentence with word breakdown, grammar patterns, vocab
export function SentenceCard({ analysis, index = 0 }: SentenceCardProps) {
  const { t } = useLanguage();
  const [showTranslation, setShowTranslation] = useState(false);
  const [translation, setTranslation] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>("");

  // AI explanation state
  const [aiExplanation, setAiExplanation] = useState<AIExplanation | null>(null);
  const [isLoadingAI, setIsLoadingAI] = useState(false);
  const [aiError, setAiError] = useState<string>("");

  const handleToggleTranslation = async () => {
    // If already showing, just toggle off
    if (showTranslation) {
      setShowTranslation(false);
      return;
    }

    // If we already have translation, just show it
    if (translation) {
      setShowTranslation(true);
      return;
    }

    // Otherwise, fetch translation
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch("/api/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: analysis.originalText }),
      });

      const result = await response.json();

      if (result.success) {
        setTranslation(result.translation);
        setShowTranslation(true);
      } else {
        setError(result.error || "Translation failed");
      }
    } catch (err) {
      setError("Failed to connect to translation service");
      console.error("Translation error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetAIExplanation = async () => {
    // If we already have explanation, do nothing
    if (aiExplanation) {
      return;
    }

    setIsLoadingAI(true);
    setAiError("");

    try {
      const response = await fetch("/api/explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sentence: analysis.originalText,
          tokens: analysis.tokens,
          grammarPatterns: analysis.grammarPatterns,
          vocabulary: analysis.vocabulary,
        }),
      });

      const result = await response.json();

      if (result.success) {
        setAiExplanation(result.aiExplanation);
      } else {
        setAiError(result.error || "AI explanation failed");
      }
    } catch (err) {
      setAiError("Failed to connect to AI service");
      console.error("AI explanation error:", err);
    } finally {
      setIsLoadingAI(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className="rounded-lg border bg-card p-6 shadow-sm hover:shadow-md transition-shadow"
    >
      {/* Header with Japanese text and JLPT level */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex-1">
          <p className="text-2xl font-medium mb-2 text-foreground">
            {analysis.originalText}
          </p>
        </div>
        <div className="flex flex-col gap-2">
          <JLPTBadge level={analysis.jlptLevel} />
          {/* Translation toggle button */}
          <button
            onClick={handleToggleTranslation}
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title={showTranslation ? "Hide translation" : "Show translation"}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Loading...</span>
              </>
            ) : showTranslation ? (
              <>
                <EyeOff className="w-3 h-3" />
                <span>Hide</span>
              </>
            ) : (
              <>
                <Eye className="w-3 h-3" />
                <span>Translate</span>
              </>
            )}
          </button>

          {/* AI Explanation button */}
          <button
            onClick={handleGetAIExplanation}
            disabled={isLoadingAI || !!aiExplanation}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-md border border-purple-300 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/30 dark:to-pink-900/30 hover:from-purple-100 hover:to-pink-100 dark:hover:from-purple-900/40 dark:hover:to-pink-900/40 text-purple-700 dark:text-purple-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title={aiExplanation ? "Explanation loaded" : "Get AI explanation"}
          >
            {isLoadingAI ? (
              <>
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Thinking...</span>
              </>
            ) : aiExplanation ? (
              <>
                <Sparkles className="w-3 h-3" />
                <span>Ready!</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3 h-3" />
                <span>Explication</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Translation display with animation */}
      <AnimatePresence>
        {showTranslation && translation && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="mb-4 overflow-hidden"
          >
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
              <p className="text-sm text-blue-900 dark:text-blue-100 italic">
                {translation}
              </p>
            </div>
          </motion.div>
        )}
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="mb-4 overflow-hidden"
          >
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
              <p className="text-sm text-red-900 dark:text-red-100">
                {error}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Word tokens with readings */}
      {analysis.tokens.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Languages className="w-4 h-4 text-muted-foreground" />
            <h3 className="text-sm font-semibold text-foreground">{t("breakdown")}</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {analysis.tokens.map((token, idx) => {
              const hasKanji = /[\u4E00-\u9FAF]/.test(token.surface);
              const shouldShowReading = hasKanji && token.reading !== token.surface && token.reading !== 'demo';

              // Extract individual kanji for WaniKani links
              const kanjiChars = hasKanji ? token.surface.match(/[\u4E00-\u9FAF]/g) || [] : [];

              return (
                <div
                  key={idx}
                  className="group relative inline-flex items-center gap-1 bg-secondary/50 rounded px-2 py-1"
                >
                  {/* Hover tooltip for reading */}
                  {shouldShowReading && (
                    <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 text-xs text-white bg-gray-900 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10">
                      {token.reading}
                    </span>
                  )}
                  <span className="text-sm font-medium">{token.surface}</span>
                  {/* WaniKani link for kanji - uses baseForm for dictionary form */}
                  {kanjiChars.length > 0 && (
                    <a
                      href={`https://www.wanikani.com/vocabulary/${encodeURIComponent(token.baseForm || token.surface)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="opacity-50 hover:opacity-100 transition-opacity ml-1"
                      title="View on WaniKani"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <ExternalLink className="w-3 h-3 text-muted-foreground hover:text-primary" />
                    </a>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Grammar patterns */}
      {analysis.grammarPatterns.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <BookOpen className="w-4 h-4 text-muted-foreground" />
            <h3 className="text-sm font-semibold text-foreground">
              {t("grammarPatterns")}
            </h3>
          </div>
          <div className="space-y-3">
            {analysis.grammarPatterns.map((pattern, idx) => (
              <div
                key={idx}
                className="flex items-start gap-2 text-sm bg-secondary/30 rounded p-3"
              >
                <JLPTBadge level={pattern.jlptLevel} className="mt-0.5" />
                <div className="flex-1">
                  <span className="font-medium">{pattern.pattern}</span>
                  <p className="text-xs text-muted-foreground mt-1">
                    {pattern.description}
                  </p>
                  {/* Example from sentence */}
                  {pattern.exampleInSentence && (
                    <div className="mt-2 px-2 py-1 bg-amber-50 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-700 rounded text-xs">
                      <span className="font-medium text-amber-900 dark:text-amber-100">
                        {pattern.exampleInSentence}
                      </span>
                    </div>
                  )}
                  {/* Pedagogical note */}
                  {pattern.pedagogicalNote && (
                    <p className="text-xs text-muted-foreground italic mt-2">
                      💡 {pattern.pedagogicalNote}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Teacher Explanation */}
      {aiExplanation && (
        <div className="mb-4">
          <details open className="group">
            <summary className="cursor-pointer list-none">
              <div className="flex items-center gap-2 mb-3 p-3 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg hover:from-purple-100 hover:to-pink-100 dark:hover:from-purple-900/30 dark:hover:to-pink-900/30 transition-colors">
                <span className="text-xl">🎓</span>
                <h3 className="text-sm font-semibold text-purple-700 dark:text-purple-300 flex-1">
                  Explication du Prof IA
                </h3>
                <span className="text-xs text-purple-600 dark:text-purple-400 group-open:rotate-180 transition-transform">
                  ▼
                </span>
              </div>
            </summary>

            <div className="space-y-4 pl-3 pr-3 pb-3">
              {/* Summary */}
              <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                {aiExplanation.summary}
              </p>

              {/* Grammar Notes */}
              {aiExplanation.grammarNotes.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm text-purple-600 dark:text-purple-400 mb-2 flex items-center gap-2">
                    <span>📝</span> Points grammaticaux
                  </h4>
                  <div className="space-y-2">
                    {aiExplanation.grammarNotes.map((note, i) => (
                      <div key={i} className="text-sm bg-white dark:bg-gray-800 p-3 rounded border border-purple-100 dark:border-purple-800">
                        <span className="font-mono text-xs bg-purple-100 dark:bg-purple-900/50 px-2 py-1 rounded text-purple-700 dark:text-purple-300">
                          {note.pattern}
                        </span>
                        <p className="text-gray-700 dark:text-gray-300 mt-2">
                          {note.explanation}
                        </p>
                        {note.example && (
                          <p className="text-xs text-gray-600 dark:text-gray-400 italic mt-2 border-l-2 border-purple-300 pl-2">
                            Exemple : {note.example}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Vocabulary Notes */}
              {aiExplanation.vocabNotes.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm text-purple-600 dark:text-purple-400 mb-2 flex items-center gap-2">
                    <span>📚</span> Nuances de vocabulaire
                  </h4>
                  <ul className="space-y-2">
                    {aiExplanation.vocabNotes.map((vocab, i) => (
                      <li key={i} className="text-sm bg-white dark:bg-gray-800 p-3 rounded border border-purple-100 dark:border-purple-800">
                        <span className="font-medium text-gray-900 dark:text-gray-100">
                          {vocab.word}
                        </span>
                        {vocab.reading && (
                          <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
                            ({vocab.reading})
                          </span>
                        )}
                        <span className="text-gray-700 dark:text-gray-300"> : {vocab.nuance}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Cultural Context */}
              {aiExplanation.culturalContext && (
                <div className="text-sm bg-blue-50 dark:bg-blue-900/30 p-3 rounded border border-blue-200 dark:border-blue-800">
                  <span className="font-medium text-blue-700 dark:text-blue-300">💡 Contexte culturel :</span>
                  <p className="text-blue-900 dark:text-blue-100 mt-1">
                    {aiExplanation.culturalContext}
                  </p>
                </div>
              )}

              {/* Register Note */}
              {aiExplanation.registerNote && (
                <div className="text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-2 rounded border border-gray-200 dark:border-gray-700">
                  <span className="font-medium">Registre :</span> {aiExplanation.registerNote}
                </div>
              )}

              {/* Study Tips */}
              {aiExplanation.studyTips && (
                <div className="text-sm bg-green-50 dark:bg-green-900/30 p-3 rounded border border-green-200 dark:border-green-800">
                  <span className="font-medium text-green-700 dark:text-green-300">📖 Conseil d'étude :</span>
                  <p className="text-green-900 dark:text-green-100 mt-1">
                    {aiExplanation.studyTips}
                  </p>
                </div>
              )}
            </div>
          </details>
        </div>
      )}

      {/* Vocabulary list */}
      {analysis.vocabulary.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <GraduationCap className="w-4 h-4 text-muted-foreground" />
            <h3 className="text-sm font-semibold text-foreground">{t("vocabulary")}</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {analysis.vocabulary.map((vocab, idx) => {
              const hasKanji = /[\u4E00-\u9FAF]/.test(vocab.word);
              const shouldShowReading = hasKanji && vocab.reading !== vocab.word && vocab.reading !== 'demo';

              return (
                <div
                  key={idx}
                  className="group flex items-start gap-2 text-sm bg-secondary/30 rounded p-2 cursor-help"
                >
                  <JLPTBadge level={vocab.jlptLevel} className="mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1">
                      <div className="font-medium truncate relative inline-block">
                        {/* Hover tooltip with reading and translation */}
                        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 text-xs text-white bg-gray-900 dark:bg-gray-800 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10 max-w-xs">
                          <div className="flex flex-col gap-1">
                            {shouldShowReading && (
                              <div className="text-gray-300 dark:text-gray-400 font-mono">
                                {vocab.reading}
                              </div>
                            )}
                            <div className="text-white font-normal">
                              {vocab.meaning}
                            </div>
                          </div>
                          {/* Tooltip arrow */}
                          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900 dark:border-t-gray-800"></div>
                        </span>
                        {vocab.word}
                      </div>
                      {/* WaniKani link - uses baseForm for dictionary form */}
                      {hasKanji && (
                        <a
                          href={`https://www.wanikani.com/vocabulary/${encodeURIComponent(vocab.baseForm || vocab.word)}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="opacity-50 hover:opacity-100 transition-opacity flex-shrink-0 ml-1"
                          title="View on WaniKani"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <ExternalLink className="w-3 h-3 text-muted-foreground hover:text-primary" />
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </motion.div>
  );
}
