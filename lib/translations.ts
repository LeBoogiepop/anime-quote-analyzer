// Translation strings for internationalization
export const translations = {
  en: {
    // Header
    appName: "Anime Quote Analyzer",
    viewOnGitHub: "View on GitHub",

    // Hero Section
    heroTitle: "Learn Japanese Through Anime",
    heroDescription: "Upload anime subtitle files to analyze JLPT levels, break down grammar patterns, and create custom Anki flashcards for effective learning.",

    // Demo Banner
    demoBanner: "✅ Python MeCab Backend Active - Real Japanese NLP analysis!",

    // Features
    jlptDetectionTitle: "JLPT Level Detection",
    jlptDetectionDesc: "Automatically detect JLPT levels (N5-N1) for vocabulary and grammar patterns in your anime subtitles.",
    grammarBreakdownTitle: "Grammar Breakdown",
    grammarBreakdownDesc: "Get detailed explanations of grammar patterns with examples and JLPT classifications.",
    ankiExportTitle: "Anki Export",
    ankiExportDesc: "Create custom flashcards with context from your favorite anime for spaced repetition learning.",

    // File Upload
    uploadTitle: "Upload Your Subtitle File",
    uploadDescription: "Drop a .srt or .ass file to get started. Try the sample file in",
    dropFileHere: "Drop your subtitle file here",
    orClickToBrowse: "or click to browse",
    supportedFormats: "Supported formats:",
    processingFile: "Processing file...",

    // Results
    analysisResults: "Analysis Results",
    showing: "Showing",
    of: "of",
    analyzedSentences: "analyzed sentences",
    totalInFile: "total in file",
    loadMoreResults: "Load More Results",

    // Sample Demo
    tryItOut: "Try it out!",
    uploadSubtitlePrompt: "Upload a subtitle file to see the magic happen, or view this sample analysis:",

    // Sentence Card
    breakdown: "Breakdown",
    grammarPatterns: "Grammar Patterns",
    vocabulary: "Vocabulary",
    explanation: "Explanation",

    // Footer
    builtWith: "Built with Next.js 14, TypeScript, Tailwind CSS, and Framer Motion",
    pythonBackend: "Python NLP backend (MeCab/fugashi) • Automatic translations via Jisho/DeepL",

    // JLPT Levels
    beginner: "Beginner",
    elementary: "Elementary",
    intermediate: "Intermediate",
    advanced: "Advanced",
    expert: "Expert",
  },
  fr: {
    // Header
    appName: "Analyseur de Citations d'Anime",
    viewOnGitHub: "Voir sur GitHub",

    // Hero Section
    heroTitle: "Apprenez le Japonais avec les Anime",
    heroDescription: "Téléchargez des fichiers de sous-titres d'anime pour analyser les niveaux JLPT, décomposer les structures grammaticales et créer des flashcards Anki personnalisées pour un apprentissage efficace.",

    // Demo Banner
    demoBanner: "✅ Backend Python MeCab Actif - Analyse NLP japonaise réelle !",

    // Features
    jlptDetectionTitle: "Détection du Niveau JLPT",
    jlptDetectionDesc: "Détectez automatiquement les niveaux JLPT (N5-N1) pour le vocabulaire et les structures grammaticales dans vos sous-titres d'anime.",
    grammarBreakdownTitle: "Analyse Grammaticale",
    grammarBreakdownDesc: "Obtenez des explications détaillées des structures grammaticales avec des exemples et des classifications JLPT.",
    ankiExportTitle: "Export Anki",
    ankiExportDesc: "Créez des flashcards personnalisées avec le contexte de vos anime préférés pour l'apprentissage par répétition espacée.",

    // File Upload
    uploadTitle: "Téléchargez Votre Fichier de Sous-titres",
    uploadDescription: "Déposez un fichier .srt ou .ass pour commencer. Essayez le fichier d'exemple dans",
    dropFileHere: "Déposez votre fichier de sous-titres ici",
    orClickToBrowse: "ou cliquez pour parcourir",
    supportedFormats: "Formats supportés :",
    processingFile: "Traitement du fichier...",

    // Results
    analysisResults: "Résultats d'Analyse",
    showing: "Affichage de",
    of: "sur",
    analyzedSentences: "phrases analysées",
    totalInFile: "total dans le fichier",
    loadMoreResults: "Charger Plus de Résultats",

    // Sample Demo
    tryItOut: "Essayez !",
    uploadSubtitlePrompt: "Téléchargez un fichier de sous-titres pour voir la magie opérer, ou consultez cet exemple d'analyse :",

    // Sentence Card
    breakdown: "Décomposition",
    grammarPatterns: "Structures Grammaticales",
    vocabulary: "Vocabulaire",
    explanation: "Explication",

    // Footer
    builtWith: "Construit avec Next.js 14, TypeScript, Tailwind CSS et Framer Motion",
    pythonBackend: "Backend Python NLP (MeCab/fugashi) • Traductions automatiques via Jisho/DeepL",

    // JLPT Levels
    beginner: "Débutant",
    elementary: "Élémentaire",
    intermediate: "Intermédiaire",
    advanced: "Avancé",
    expert: "Expert",
  },
} as const;

export type Language = keyof typeof translations;
export type TranslationKeys = keyof typeof translations.en;
