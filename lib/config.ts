/**
 * Centralized configuration for the application.
 * 
 * This module provides a single source of truth for backend URL and other
 * configuration values, making it easier to maintain and update.
 */

/**
 * Get the Python backend URL from environment variables.
 * Defaults to http://localhost:8000 if not set.
 */
export function getBackendUrl(): string {
  return process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';
}

/**
 * Configuration object for backend API calls.
 */
export const backendConfig = {
  /**
   * Base URL for the Python FastAPI backend
   */
  url: getBackendUrl(),
  
  /**
   * Default timeout for API requests (in milliseconds)
   */
  defaultTimeout: 10000, // 10 seconds
  
  /**
   * Timeout for AI explanation requests (longer, in milliseconds)
   */
  aiExplanationTimeout: 15000, // 15 seconds
  
  /**
   * Timeout for translation requests (DeepL can be slow, in milliseconds)
   */
  translationTimeout: 20000, // 20 seconds
} as const;

