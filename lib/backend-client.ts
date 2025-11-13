/**
 * Backend API client utilities.
 * 
 * Centralizes backend API calls with consistent error handling,
 * timeout management, and logging.
 */

import { backendConfig } from "./config";

export interface BackendError {
  name: string;
  message?: string;
  code?: string;
}

export interface BackendCallOptions {
  /**
   * Custom timeout in milliseconds (overrides default)
   */
  timeout?: number;
  
  /**
   * Custom error message for timeout
   */
  timeoutMessage?: string;
  
  /**
   * Custom error message for connection refused
   */
  connectionErrorMessage?: string;
}

/**
 * Make a request to the Python backend API.
 * 
 * @param endpoint - API endpoint (e.g., '/analyze', '/explain')
 * @param method - HTTP method (default: 'POST')
 * @param body - Request body object (will be JSON stringified)
 * @param options - Additional options for the request
 * @returns Promise with the response data
 * @throws Error if the request fails
 */
export async function callBackend<T = unknown>(
  endpoint: string,
  method: 'GET' | 'POST' = 'POST',
  body?: unknown,
  options: BackendCallOptions = {}
): Promise<T> {
  const backendUrl = backendConfig.url;
  const timeout = options.timeout ?? backendConfig.defaultTimeout;
  const startTime = Date.now();

  // Log the request
  const endpointName = endpoint.replace('/', '').replace('-', ' ');
  console.log(`Calling backend ${endpointName} at: ${backendUrl}`);

  try {
    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(`${backendUrl}${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = `Backend returned ${response.status}: ${errorData.detail || response.statusText}`;
      const error = new Error(errorMessage);
      // Add status code to error for better handling
      (error as Error & { status?: number }).status = response.status;
      throw error;
    }

    const result = await response.json() as T;
    const duration = Date.now() - startTime;

    console.log(`✓ Backend ${endpointName} complete in ${duration}ms`);

    return result;
  } catch (error: unknown) {
    const backendError = error as BackendError;
    const duration = Date.now() - startTime;

    // Handle timeout
    if (backendError.name === 'AbortError') {
      console.error(`Backend request timed out after ${timeout / 1000} seconds`);
      throw new BackendTimeoutError(
        options.timeoutMessage || 
        `Backend request timed out after ${timeout / 1000} seconds`
      );
    }

    // Handle connection refused
    if (
      backendError.message?.includes('fetch failed') || 
      backendError.code === 'ECONNREFUSED'
    ) {
      console.error('Python backend is not running');
      throw new BackendConnectionError(
        options.connectionErrorMessage || 
        'Python backend is not running. Start it with: cd backend && python server.py'
      );
    }

    // Re-throw other errors
    console.error(`Backend error after ${duration}ms:`, backendError.message || 'Unknown error');
    throw error;
  }
}

/**
 * Custom error class for backend timeouts
 */
export class BackendTimeoutError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'BackendTimeoutError';
  }
}

/**
 * Custom error class for backend connection errors
 */
export class BackendConnectionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'BackendConnectionError';
  }
}

