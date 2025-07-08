// Application constants

export const APP_NAME = 'LLM Platform'
export const APP_VERSION = '1.0.0'
export const APP_DESCRIPTION = '企业级大模型克隆平台'

// API constants
export const API_BASE_URL = '/api/v1'
export const REQUEST_TIMEOUT = 30000

// Storage keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  THEME_MODE: 'theme_mode',
  SELECTED_MODEL: 'selected_model',
  CHAT_HISTORY: 'chat_history',
  USER_PREFERENCES: 'user_preferences'
} as const

// Model providers
export const MODEL_PROVIDERS = {
  OPENAI: 'OpenAI',
  DEEPSEEK: 'DeepSeek',
  ANTHROPIC: 'Anthropic',
  GOOGLE: 'Google',
  META: 'Meta',
  MICROSOFT: 'Microsoft'
} as const

// Chat message roles
export const MESSAGE_ROLES = {
  SYSTEM: 'system',
  USER: 'user',
  ASSISTANT: 'assistant'
} as const

// API status codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500
} as const

// User roles
export const USER_ROLES = {
  USER: 'user',
  ADMIN: 'admin'
} as const

// Theme modes
export const THEME_MODES = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto'
} as const

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZES: [10, 20, 50, 100]
} as const

// Chart colors
export const CHART_COLORS = [
  '#6366f1',
  '#06b6d4',
  '#10b981',
  '#f59e0b',
  '#ef4444',
  '#8b5cf6',
  '#06b6d4',
  '#84cc16',
  '#f97316',
  '#ec4899'
] as const

// File size limits
export const FILE_LIMITS = {
  AVATAR_MAX_SIZE: 2 * 1024 * 1024, // 2MB
  DOCUMENT_MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  ALLOWED_DOCUMENT_TYPES: ['application/pdf', 'text/plain', 'text/markdown']
} as const

// Rate limiting
export const RATE_LIMITS = {
  DEFAULT_PER_MINUTE: 60,
  CHAT_PER_MINUTE: 20,
  API_KEY_CREATION_PER_DAY: 10
} as const

// Validation rules
export const VALIDATION = {
  USERNAME_MIN_LENGTH: 3,
  USERNAME_MAX_LENGTH: 50,
  PASSWORD_MIN_LENGTH: 6,
  PASSWORD_MAX_LENGTH: 128,
  EMAIL_MAX_LENGTH: 255,
  NAME_MAX_LENGTH: 100,
  DESCRIPTION_MAX_LENGTH: 500,
  API_KEY_NAME_MAX_LENGTH: 100
} as const