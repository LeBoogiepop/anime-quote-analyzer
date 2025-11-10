"use client";

import { useState } from "react";
import { FileUploader } from "@/components/FileUploader";
import { SentenceCard } from "@/components/SentenceCard";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { motion } from "framer-motion";
import { Sparkles, BookOpen, Download, Github } from "lucide-react";
import { type SubtitleEntry, type SentenceAnalysis } from "@/lib/types";
import { useLanguage } from "@/lib/LanguageContext";

export default function Home() {
  const { t } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [subtitles, setSubtitles] = useState<SubtitleEntry[]>([]);
  const [analyses, setAnalyses] = useState<SentenceAnalysis[]>([]);
  const [displayCount, setDisplayCount] = useState(5);

  const handleFileUpload = async (file: File) => {
    console.log('Starting file upload:', file.name);
    setLoading(true);
    setSubtitles([]);
    setAnalyses([]);

    try {
      // Parse subtitle file
      const formData = new FormData();
      formData.append("file", file);

      const parseResponse = await fetch("/api/parse", {
        method: "POST",
        body: formData,
      });

      const parseData = await parseResponse.json();
      console.log('Parsed entries:', parseData.entries?.length);

      if (!parseData.success) {
        alert(parseData.error || "Failed to parse subtitle file");
        setLoading(false);
        return;
      }

      setSubtitles(parseData.entries);

      // Analyze first 5 entries (for demo purposes)
      const entriesToAnalyze = parseData.entries.slice(0, 5);
      const analysisPromises = entriesToAnalyze.map((entry: SubtitleEntry) =>
        fetch("/api/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: entry.text }),
        }).then((res) => res.json())
      );

      const analysisResults = await Promise.all(analysisPromises);
      const validAnalyses = analysisResults
        .filter((result) => result.success)
        .map((result) => result.analysis);

      setAnalyses(validAnalyses);
      setDisplayCount(5); // Reset display count when new file is uploaded
    } catch (error) {
      console.error("Error processing file:", error);
      alert("Failed to process file. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = () => {
    setDisplayCount(prev => Math.min(prev + 5, analyses.length));
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-secondary/20">
      {/* Header */}
      <header className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-2"
            >
              <Sparkles className="w-6 h-6 text-primary" />
              <h1 className="text-2xl font-bold text-foreground">
                {t("appName")}
              </h1>
            </motion.div>
            <div className="flex items-center gap-4">
              <LanguageSwitcher />
              <motion.a
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                href="https://github.com/LeBoogiepop/anime-quote-analyzer"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                <Github className="w-5 h-5" />
                <span className="hidden sm:inline">{t("viewOnGitHub")}</span>
              </motion.a>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            {t("heroTitle")}
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            {t("heroDescription")}
          </p>
        </motion.div>

        {/* Backend Status Banner */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="max-w-3xl mx-auto mb-8"
        >
          <div className="bg-green-50 dark:bg-green-900/20 border-2 border-green-200 dark:border-green-800 rounded-lg p-4 text-center">
            <p className="text-sm font-medium text-green-800 dark:text-green-200">
              {t("demoBanner")}
            </p>
          </div>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12"
        >
          <div className="bg-card border rounded-lg p-6 hover:shadow-lg transition-shadow">
            <BookOpen className="w-10 h-10 text-primary mb-4" />
            <h3 className="text-lg font-semibold mb-2">{t("jlptDetectionTitle")}</h3>
            <p className="text-sm text-muted-foreground">
              {t("jlptDetectionDesc")}
            </p>
          </div>
          <div className="bg-card border rounded-lg p-6 hover:shadow-lg transition-shadow">
            <Sparkles className="w-10 h-10 text-primary mb-4" />
            <h3 className="text-lg font-semibold mb-2">{t("grammarBreakdownTitle")}</h3>
            <p className="text-sm text-muted-foreground">
              {t("grammarBreakdownDesc")}
            </p>
          </div>
          <div className="bg-card border rounded-lg p-6 hover:shadow-lg transition-shadow">
            <Download className="w-10 h-10 text-primary mb-4" />
            <h3 className="text-lg font-semibold mb-2">{t("ankiExportTitle")}</h3>
            <p className="text-sm text-muted-foreground">
              {t("ankiExportDesc")}
            </p>
          </div>
        </motion.div>

        {/* File Uploader */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="max-w-3xl mx-auto mb-12"
        >
          <h3 className="text-xl font-bold text-foreground mb-4 text-center">
            {t("uploadTitle")}
          </h3>
          <p className="text-sm text-muted-foreground text-center mb-4">
            {t("uploadDescription")} <code className="bg-secondary px-1 py-0.5 rounded">public/test.srt</code>
          </p>
          <FileUploader onFileUpload={handleFileUpload} isLoading={loading} />
        </motion.div>

        {/* Analysis Results */}
        {analyses.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="max-w-4xl mx-auto"
          >
            <h3 className="text-2xl font-bold text-foreground mb-6">
              {t("analysisResults")}
            </h3>
            <div className="space-y-6">
              {analyses.slice(0, displayCount).map((analysis, index) => (
                <SentenceCard key={index} analysis={analysis} index={index} />
              ))}
            </div>
            <div className="mt-8 text-center">
              <p className="text-sm text-muted-foreground mb-4">
                {t("showing")} {Math.min(displayCount, analyses.length)} {t("of")} {analyses.length} {t("analyzedSentences")}
                {subtitles.length > analyses.length && ` (${subtitles.length} ${t("totalInFile")})`}
              </p>
              {displayCount < analyses.length && (
                <button
                  onClick={handleLoadMore}
                  className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
                >
                  {t("loadMoreResults")}
                </button>
              )}
            </div>
          </motion.div>
        )}

        {/* Empty State - Demo Data */}
        {analyses.length === 0 && !loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="max-w-4xl mx-auto"
          >
            <h3 className="text-2xl font-bold text-foreground mb-6 text-center">
              {t("tryItOut")}
            </h3>
            <p className="text-center text-muted-foreground mb-6">
              {t("uploadSubtitlePrompt")}
            </p>
            <SentenceCard
              analysis={{
                originalText: "私は日本語を勉強しています。",
                tokens: [
                  {
                    surface: "私",
                    reading: "わたし",
                    partOfSpeech: "Noun",
                    baseForm: "私",
                  },
                  {
                    surface: "は",
                    reading: "は",
                    partOfSpeech: "Particle",
                    baseForm: "は",
                  },
                  {
                    surface: "日本語",
                    reading: "にほんご",
                    partOfSpeech: "Noun",
                    baseForm: "日本語",
                  },
                  {
                    surface: "を",
                    reading: "を",
                    partOfSpeech: "Particle",
                    baseForm: "を",
                  },
                  {
                    surface: "勉強",
                    reading: "べんきょう",
                    partOfSpeech: "Verb",
                    baseForm: "勉強する",
                  },
                  {
                    surface: "して",
                    reading: "して",
                    partOfSpeech: "Verb",
                    baseForm: "する",
                  },
                  {
                    surface: "います",
                    reading: "います",
                    partOfSpeech: "Verb",
                    baseForm: "いる",
                  },
                ],
                jlptLevel: "N5",
                grammarPatterns: [
                  {
                    pattern: "～ています",
                    description:
                      "Present progressive/continuous form. Used to express ongoing actions or states.",
                    jlptLevel: "N5",
                    example: "食べています (I am eating)",
                  },
                ],
                vocabulary: [
                  {
                    word: "私",
                    reading: "わたし",
                    meaning: "I, me",
                    jlptLevel: "N5",
                  },
                  {
                    word: "日本語",
                    reading: "にほんご",
                    meaning: "Japanese language",
                    jlptLevel: "N5",
                  },
                  {
                    word: "勉強する",
                    reading: "べんきょうする",
                    meaning: "to study",
                    jlptLevel: "N5",
                  },
                ],
              }}
            />
          </motion.div>
        )}
      </section>

      {/* Footer */}
      <footer className="border-t mt-20 py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>
            {t("builtWith")}
          </p>
          <p className="mt-2">
            {t("pythonBackend")}
          </p>
        </div>
      </footer>
    </div>
  );
}
