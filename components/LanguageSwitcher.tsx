"use client";

import { useLanguage } from "@/lib/LanguageContext";
import { Languages } from "lucide-react";

// Language switcher component for EN/FR toggle
export function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();

  const toggleLanguage = () => {
    setLanguage(language === "en" ? "fr" : "en");
  };

  return (
    <button
      onClick={toggleLanguage}
      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
      aria-label="Switch language"
    >
      <Languages className="w-4 h-4" />
      <span className="uppercase">{language}</span>
    </button>
  );
}
