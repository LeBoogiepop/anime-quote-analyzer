"use client";

import { useState } from "react";
import { FileUploader } from "@/components/FileUploader";
import { SentenceCard } from "@/components/SentenceCard";
import { motion } from "framer-motion";
import { Sparkles, BookOpen, Download, Github } from "lucide-react";
import { type SubtitleEntry, type SentenceAnalysis } from "@/lib/types";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [subtitles, setSubtitles] = useState<SubtitleEntry[]>([]);
  const [analyses, setAnalyses] = useState<SentenceAnalysis[]>([]);

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
    } catch (error) {
      console.error("Error processing file:", error);
      alert("Failed to process file. Please try again.");
    } finally {
      setLoading(false);
    }
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
                Anime Quote Analyzer
              </h1>
            </motion.div>
            <motion.a
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <Github className="w-5 h-5" />
              <span className="hidden sm:inline">View on GitHub</span>
            </motion.a>
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
            Learn Japanese Through Anime
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload anime subtitle files to analyze JLPT levels, break down grammar
            patterns, and create custom Anki flashcards for effective learning.
          </p>
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
            <h3 className="text-lg font-semibold mb-2">JLPT Level Detection</h3>
            <p className="text-sm text-muted-foreground">
              Automatically detect JLPT levels (N5-N1) for vocabulary and grammar
              patterns in your anime subtitles.
            </p>
          </div>
          <div className="bg-card border rounded-lg p-6 hover:shadow-lg transition-shadow">
            <Sparkles className="w-10 h-10 text-primary mb-4" />
            <h3 className="text-lg font-semibold mb-2">Grammar Breakdown</h3>
            <p className="text-sm text-muted-foreground">
              Get detailed explanations of grammar patterns with examples and JLPT
              classifications.
            </p>
          </div>
          <div className="bg-card border rounded-lg p-6 hover:shadow-lg transition-shadow">
            <Download className="w-10 h-10 text-primary mb-4" />
            <h3 className="text-lg font-semibold mb-2">Anki Export</h3>
            <p className="text-sm text-muted-foreground">
              Create custom flashcards with context from your favorite anime for
              spaced repetition learning.
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
              Analysis Results
            </h3>
            <div className="space-y-6">
              {analyses.map((analysis, index) => (
                <SentenceCard key={index} analysis={analysis} index={index} />
              ))}
            </div>
            {subtitles.length > 5 && (
              <p className="text-center text-sm text-muted-foreground mt-6">
                Showing first 5 of {subtitles.length} entries (demo mode)
              </p>
            )}
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
              Try it out!
            </h3>
            <p className="text-center text-muted-foreground mb-6">
              Upload a subtitle file to see the magic happen, or view this sample
              analysis:
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
            Built with Next.js 14, TypeScript, Tailwind CSS, and Framer Motion
          </p>
          <p className="mt-2">
            Python NLP backend integration coming soon (MeCab/fugashi)
          </p>
        </div>
      </footer>
    </div>
  );
}
