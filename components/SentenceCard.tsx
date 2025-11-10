"use client";

import { type SentenceAnalysis } from "@/lib/types";
import { JLPTBadge } from "./JLPTBadge";
import { motion } from "framer-motion";
import { BookOpen, GraduationCap, Languages, ExternalLink } from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";

interface SentenceCardProps {
  analysis: SentenceAnalysis;
  index?: number;
}

// Displays analyzed Japanese sentence with word breakdown, grammar patterns, vocab
export function SentenceCard({ analysis, index = 0 }: SentenceCardProps) {
  const { t } = useLanguage();

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
        <JLPTBadge level={analysis.jlptLevel} />
      </div>

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
                  {/* WaniKani link for kanji */}
                  {kanjiChars.length > 0 && (
                    <a
                      href={`https://www.wanikani.com/vocabulary/${encodeURIComponent(token.surface)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="opacity-0 group-hover:opacity-70 hover:opacity-100 transition-opacity"
                      title="View on WaniKani"
                    >
                      <ExternalLink className="w-3 h-3 text-muted-foreground" />
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
          <div className="space-y-2">
            {analysis.grammarPatterns.map((pattern, idx) => (
              <div
                key={idx}
                className="flex items-start gap-2 text-sm bg-secondary/30 rounded p-2"
              >
                <JLPTBadge level={pattern.jlptLevel} className="mt-0.5" />
                <div>
                  <span className="font-medium">{pattern.pattern}</span>
                  <p className="text-xs text-muted-foreground mt-1">
                    {pattern.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
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
                  className="group flex items-start gap-2 text-sm bg-secondary/30 rounded p-2"
                >
                  <JLPTBadge level={vocab.jlptLevel} className="mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1">
                      <div className="font-medium truncate">
                        {vocab.word}
                        {shouldShowReading && (
                          <>
                            {" "}
                            <span className="text-muted-foreground">
                              ({vocab.reading})
                            </span>
                          </>
                        )}
                      </div>
                      {/* WaniKani link */}
                      {hasKanji && (
                        <a
                          href={`https://www.wanikani.com/vocabulary/${encodeURIComponent(vocab.word)}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="opacity-0 group-hover:opacity-70 hover:opacity-100 transition-opacity flex-shrink-0"
                          title="View on WaniKani"
                        >
                          <ExternalLink className="w-3 h-3 text-muted-foreground" />
                        </a>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground truncate">
                      {vocab.meaning}
                    </p>
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
