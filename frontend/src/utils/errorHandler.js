import { useToast } from 'vue-toast-notification';

// Error types for consistent categorization
export const ErrorTypes = {
  NETWORK: 'NETWORK',
  AUTH: 'AUTH',
  VALIDATION: 'VALIDATION',
  RUNTIME: 'RUNTIME',
  UNKNOWN: 'UNKNOWN'
};

// User-friendly messages for common errors
const errorMessages = {
  [ErrorTypes.NETWORK]: 'Network connection issue. Please check your internet connection.',
  [ErrorTypes.AUTH]: 'Authentication error. Please try logging in again.',
  [ErrorTypes.VALIDATION]: 'Please check your input and try again.',
  [ErrorTypes.RUNTIME]: 'Something went wrong. Please try again.',
  [ErrorTypes.UNKNOWN]: 'An unexpected error occurred. Please try again.'
};

/**
 * Determines the type of error based on the error object
 * @param {Error} error - The error object
 * @returns {string} The error type
 */
const getErrorType = (error) => {
  if (!navigator.onLine || error?.message?.includes('network') || error?.name === 'NetworkError') {
    return ErrorTypes.NETWORK;
  }
  if (error?.code?.startsWith('auth/') || error?.message?.includes('auth')) {
    return ErrorTypes.AUTH;
  }
  if (error?.validation || error?.name === 'ValidationError') {
    return ErrorTypes.VALIDATION;
  }
  if (error instanceof Error) {
    return ErrorTypes.RUNTIME;
  }
  return ErrorTypes.UNKNOWN;
};

/**
 * Gets a user-friendly message based on the error
 * @param {Error} error - The error object
 * @returns {string} User-friendly error message
 */
const getUserFriendlyMessage = (error) => {
  const errorType = getErrorType(error);
  return errorMessages[errorType] || errorMessages[ErrorTypes.UNKNOWN];
};

/**
 * Global error handler
 * @param {Error} error - The error object
 * @param {string} context - Context where the error occurred
 * @param {Object} options - Additional options for error handling
 */
export const handleError = (error, context = '', options = {}) => {
  // Log error with context
  console.error(`[${context}]`, error);

  // Get user-friendly message
  const message = options.message || getUserFriendlyMessage(error);

  // Show toast notification
  const toast = useToast();
  toast.error(message, {
    duration: 3000,
    dismissible: true,
    position: 'top-right',
    ...options.toastOptions
  });

  // Return error type for potential specific handling
  return getErrorType(error);
};
