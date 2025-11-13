"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Loader2, Check, ChevronDown } from "lucide-react";
import { type SentenceAnalysis } from "@/lib/types";
import { useLanguage } from "@/lib/LanguageContext";

interface AnkiExportModalProps {
  analysis: SentenceAnalysis;
  isOpen: boolean;
  onClose: () => void;
  onExport: (config: AnkiExportConfig) => Promise<void>;
}

export interface AnkiExportConfig {
  deckName: string;
  modelName: string;
  selectedVocab: string[]; // Word IDs to include
  includeGrammar: boolean;
  includeTranslation: boolean;
}

const DEFAULT_DECK = "Japanese::Anime Quotes";
const DEFAULT_MODEL = "Japanese Sentence";

export function AnkiExportModal({
  analysis,
  isOpen,
  onClose,
  onExport,
}: AnkiExportModalProps) {
  const { t } = useLanguage();
  const [deckName, setDeckName] = useState(DEFAULT_DECK);
  const [modelName, setModelName] = useState(DEFAULT_MODEL);
  const [selectedVocab, setSelectedVocab] = useState<string[]>(
    analysis.vocabulary.map((v) => v.word)
  );
  const [includeGrammar, setIncludeGrammar] = useState(true);
  const [includeTranslation, setIncludeTranslation] = useState(true);
  const [isLoadingDecks, setIsLoadingDecks] = useState(false);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [availableDecks, setAvailableDecks] = useState<string[]>([]);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [showDeckDropdown, setShowDeckDropdown] = useState(false);
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const deckDropdownRef = useRef<HTMLDivElement>(null);
  const modelDropdownRef = useRef<HTMLDivElement>(null);

  // Load decks and models when modal opens
  useEffect(() => {
    if (isOpen) {
      loadDecks();
      loadModels();
    }
  }, [isOpen]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        deckDropdownRef.current &&
        !deckDropdownRef.current.contains(event.target as Node)
      ) {
        setShowDeckDropdown(false);
      }
      if (
        modelDropdownRef.current &&
        !modelDropdownRef.current.contains(event.target as Node)
      ) {
        setShowModelDropdown(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const loadDecks = async () => {
    setIsLoadingDecks(true);
    try {
      const response = await fetch("/api/anki/decks");
      if (response.ok) {
        const data = await response.json();
        setAvailableDecks(data.decks || []);
      }
    } catch (error) {
      console.error("Failed to load decks:", error);
    } finally {
      setIsLoadingDecks(false);
    }
  };

  const loadModels = async () => {
    setIsLoadingModels(true);
    try {
      const response = await fetch("/api/anki/models");
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data.models || []);
      }
    } catch (error) {
      console.error("Failed to load models:", error);
    } finally {
      setIsLoadingModels(false);
    }
  };

  const toggleVocab = (word: string) => {
    setSelectedVocab((prev) =>
      prev.includes(word)
        ? prev.filter((w) => w !== word)
        : [...prev, word]
    );
  };

  const handleExport = async () => {
    if (selectedVocab.length === 0) {
      alert(t("ankiSelectVocab"));
      return;
    }

    setIsExporting(true);
    try {
      await onExport({
        deckName,
        modelName,
        selectedVocab,
        includeGrammar,
        includeTranslation,
      });
      onClose();
    } catch (error) {
      console.error("Export failed:", error);
    } finally {
      setIsExporting(false);
    }
  };

  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      <div 
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        onClick={handleBackdropClick}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-card border rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b">
            <h2 className="text-xl font-bold">{t("exportToAnki")}</h2>
            <button
              onClick={onClose}
              className="p-1 rounded hover:bg-secondary transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* Deck Selection */}
            <div>
              <label className="block text-sm font-medium mb-2">
                {t("ankiDeck")}
              </label>
              <div className="relative" ref={deckDropdownRef}>
                <button
                  onClick={() => setShowDeckDropdown(!showDeckDropdown)}
                  className="w-full flex items-center justify-between px-3 py-2 border rounded-md bg-background hover:bg-accent transition-colors"
                  disabled={isLoadingDecks}
                >
                  <span>{deckName}</span>
                  {isLoadingDecks ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </button>
                {showDeckDropdown && (
                  <div className="absolute z-10 w-full mt-1 bg-background border rounded-md shadow-lg max-h-60 overflow-y-auto">
                    {availableDecks.map((deck) => (
                      <button
                        key={deck}
                        onClick={() => {
                          setDeckName(deck);
                          setShowDeckDropdown(false);
                        }}
                        className="w-full text-left px-3 py-2 hover:bg-accent transition-colors"
                      >
                        {deck}
                      </button>
                    ))}
                    <div className="border-t p-2">
                      <input
                        type="text"
                        placeholder={t("ankiNewDeck")}
                        value={deckName}
                        onChange={(e) => setDeckName(e.target.value)}
                        className="w-full px-2 py-1 text-sm border rounded"
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            setShowDeckDropdown(false);
                          }
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Model Selection */}
            <div>
              <label className="block text-sm font-medium mb-2">
                {t("ankiModel")}
              </label>
              <div className="relative" ref={modelDropdownRef}>
                <button
                  onClick={() => setShowModelDropdown(!showModelDropdown)}
                  className="w-full flex items-center justify-between px-3 py-2 border rounded-md bg-background hover:bg-accent transition-colors"
                  disabled={isLoadingModels}
                >
                  <span>{modelName}</span>
                  {isLoadingModels ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </button>
                {showModelDropdown && (
                  <div className="absolute z-10 w-full mt-1 bg-background border rounded-md shadow-lg max-h-60 overflow-y-auto">
                    {availableModels.map((model) => (
                      <button
                        key={model}
                        onClick={() => {
                          setModelName(model);
                          setShowModelDropdown(false);
                        }}
                        className="w-full text-left px-3 py-2 hover:bg-accent transition-colors"
                      >
                        {model}
                      </button>
                    ))}
                    <div className="border-t p-2">
                      <input
                        type="text"
                        placeholder={t("ankiNewModel")}
                        value={modelName}
                        onChange={(e) => setModelName(e.target.value)}
                        className="w-full px-2 py-1 text-sm border rounded"
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            setShowModelDropdown(false);
                          }
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Vocabulary Selection */}
            <div>
              <label className="block text-sm font-medium mb-2">
                {t("ankiSelectVocab")} ({selectedVocab.length}/{analysis.vocabulary.length})
              </label>
              <div className="border rounded-md p-3 max-h-48 overflow-y-auto space-y-2">
                {analysis.vocabulary.map((vocab) => (
                  <label
                    key={vocab.word}
                    className="flex items-center gap-2 p-2 rounded hover:bg-secondary cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedVocab.includes(vocab.word)}
                      onChange={() => toggleVocab(vocab.word)}
                      className="w-4 h-4"
                    />
                    <div className="flex-1">
                      <span className="font-medium">{vocab.word}</span>
                      <span className="text-sm text-muted-foreground ml-2">
                        ({vocab.reading}) - {vocab.meaning}
                      </span>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Options */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeGrammar}
                  onChange={(e) => setIncludeGrammar(e.target.checked)}
                  className="w-4 h-4"
                />
                <span>{t("ankiIncludeGrammar")}</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeTranslation}
                  onChange={(e) => setIncludeTranslation(e.target.checked)}
                  className="w-4 h-4"
                />
                <span>{t("ankiIncludeTranslation")}</span>
              </label>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-2 p-4 border-t">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm border rounded-md hover:bg-secondary transition-colors"
            >
              {t("cancel")}
            </button>
            <button
              onClick={handleExport}
              disabled={isExporting || selectedVocab.length === 0}
              className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isExporting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>{t("exportingToAnki")}</span>
                </>
              ) : (
                <span>{t("export")}</span>
              )}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}

