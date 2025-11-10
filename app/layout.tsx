import type { Metadata } from "next";
import "./globals.css";
import { LanguageProvider } from "@/lib/LanguageContext";

export const metadata: Metadata = {
  title: "Anime Quote Analyzer - Learn Japanese Through Anime",
  description: "Analyze anime subtitles, detect JLPT levels, break down grammar patterns, and create Anki flashcards for effective Japanese learning.",
  keywords: ["Japanese", "anime", "JLPT", "language learning", "subtitles", "Anki"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
