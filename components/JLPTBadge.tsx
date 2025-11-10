import { type JLPTLevel } from "@/lib/types";
import { cn } from "@/lib/utils";

interface JLPTBadgeProps {
  level: JLPTLevel;
  className?: string;
}

/**
 * Badge component to display JLPT level with color coding
 * N5 (Beginner) -> N1 (Advanced)
 */
export function JLPTBadge({ level, className }: JLPTBadgeProps) {
  // Color mapping based on JLPT level
  const levelColors = {
    N5: "bg-green-100 text-green-800 border-green-300 dark:bg-green-900 dark:text-green-200",
    N4: "bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900 dark:text-blue-200",
    N3: "bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900 dark:text-yellow-200",
    N2: "bg-orange-100 text-orange-800 border-orange-300 dark:bg-orange-900 dark:text-orange-200",
    N1: "bg-red-100 text-red-800 border-red-300 dark:bg-red-900 dark:text-red-200",
  };

  const levelDescriptions = {
    N5: "Beginner",
    N4: "Elementary",
    N3: "Intermediate",
    N2: "Advanced",
    N1: "Expert",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold transition-all",
        levelColors[level],
        className
      )}
      title={`JLPT ${level} - ${levelDescriptions[level]}`}
    >
      {level}
    </span>
  );
}
