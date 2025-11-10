# 🎌 Anime Quote Analyzer

A modern web application that helps Japanese learners analyze anime subtitles, detect JLPT levels, break down grammar patterns, and create custom Anki flashcards for effective language learning.

[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3-38bdf8)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

## 🚀 Features

- **📁 Subtitle Parsing**: Upload and parse anime subtitle files (.srt, .ass formats)
- **📊 JLPT Level Detection**: Automatically detect JLPT levels (N5 to N1) for vocabulary and grammar
- **📖 Grammar Breakdown**: Detailed analysis of grammar patterns with explanations
- **📝 Vocabulary Analysis**: Extract and categorize vocabulary with readings and meanings
- **🎴 Anki Export**: Generate exportable flashcards for spaced repetition learning (coming soon)
- **📱 Responsive Design**: Mobile-first design with smooth animations
- **🎨 Modern UI**: Built with Tailwind CSS and shadcn/ui components

## 🛠️ Tech Stack

### Frontend
- **Framework**: [Next.js 14](https://nextjs.org/) (App Router)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **UI Components**: [shadcn/ui](https://ui.shadcn.com/)
- **Animations**: [Framer Motion](https://www.framer.com/motion/)
- **Icons**: [Lucide React](https://lucide.dev/)

### Backend (Planned)
- **NLP Processing**: Python with MeCab/fugashi for Japanese tokenization
- **Database**: Supabase (to be integrated)

## 📁 Project Structure

```
anime-quote-analyzer/
├── app/                    # Next.js app directory
│   ├── api/               # API routes
│   │   ├── parse/         # Subtitle parsing endpoint
│   │   └── analyze/       # Japanese text analysis endpoint
│   ├── globals.css        # Global styles with Tailwind
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Landing page
├── components/            # React components
│   ├── FileUploader.tsx   # Drag & drop file upload
│   ├── SentenceCard.tsx   # Display analyzed sentences
│   └── JLPTBadge.tsx      # JLPT level indicator
├── lib/                   # Utilities and helpers
│   ├── types.ts           # TypeScript type definitions
│   └── utils.ts           # Utility functions
├── python/                # Python NLP processing
│   ├── analyzer.py        # Japanese text analyzer (stub)
│   └── requirements.txt   # Python dependencies
└── public/                # Static assets
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Python 3.8+ (for NLP features, coming soon)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/anime-quote-analyzer.git
   cd anime-quote-analyzer
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

4. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Python Backend Setup (Coming Soon)

```bash
cd python
pip install -r requirements.txt
```

## 📖 Usage

1. **Upload a subtitle file**: Drag and drop or click to browse for .srt or .ass files
2. **View analysis**: See parsed sentences with JLPT levels and grammar breakdowns
3. **Export to Anki**: Generate flashcards for your learning (feature in development)

## 🎯 Roadmap

### Phase 1: Foundation ✅
- [x] Next.js 14 project setup with TypeScript
- [x] Tailwind CSS + shadcn/ui configuration
- [x] Core components (FileUploader, SentenceCard, JLPTBadge)
- [x] API routes for parsing and analysis
- [x] Landing page with demo

### Phase 2: NLP Integration 🚧
- [ ] Integrate MeCab/fugashi for accurate tokenization
- [ ] Implement JLPT level detection algorithm
- [ ] Grammar pattern recognition
- [ ] Vocabulary database integration

### Phase 3: Enhanced Features 📋
- [ ] Anki flashcard export (.apkg format)
- [ ] User authentication and progress tracking
- [ ] Supabase database integration
- [ ] Sentence audio playback
- [ ] Customizable learning preferences

### Phase 4: Polish & Deploy 🎨
- [ ] Advanced search and filtering
- [ ] Dark mode support
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Production deployment

## 🏗️ Development

### Build for production
```bash
npm run build
npm start
```

### Linting
```bash
npm run lint
```

### Type checking
```bash
npx tsc --noEmit
```

## 🤝 Contributing

Contributions are welcome! This is a portfolio project, but feel free to:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Japanese language processing powered by MeCab/fugashi
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Inspiration from Japanese learning communities

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This project is currently in active development. The Python NLP backend is planned for Phase 2. Current implementation uses mock data for demonstration purposes.

Made with ❤️ for Japanese learners worldwide
