"use client";

import { type SentenceAnalysis } from "@/lib/types";
import { JLPTBadge } from "./JLPTBadge";
import { motion } from "framer-motion";
import { BookOpen, GraduationCap, Languages } from "lucide-react";

interface SentenceCardProps {
  analysis: SentenceAnalysis;
  index?: number;
}

/**
 * Card component to display analyzed Japanese sentence with breakdown
 * Shows original text, tokens, JLPT level, grammar patterns, and vocabulary
 */
export function SentenceCard({ analysis, index = 0 }: SentenceCardProps) {
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
            <h3 className="text-sm font-semibold text-foreground">Breakdown</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {analysis.tokens.map((token, idx) => (
              <div
                key={idx}
                className="inline-flex flex-col items-center bg-secondary/50 rounded px-2 py-1"
              >
                <span className="text-xs text-muted-foreground">
                  {token.reading}
                </span>
                <span className="text-sm font-medium">{token.surface}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Grammar patterns */}
      {analysis.grammarPatterns.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <BookOpen className="w-4 h-4 text-muted-foreground" />
            <h3 className="text-sm font-semibold text-foreground">
              Grammar Patterns
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
            <h3 className="text-sm font-semibold text-foreground">Vocabulary</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {analysis.vocabulary.map((vocab, idx) => (
              <div
                key={idx}
                className="flex items-start gap-2 text-sm bg-secondary/30 rounded p-2"
              >
                <JLPTBadge level={vocab.jlptLevel} className="mt-0.5" />
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">
                    {vocab.word}{" "}
                    <span className="text-muted-foreground">
                      ({vocab.reading})
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground truncate">
                    {vocab.meaning}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
