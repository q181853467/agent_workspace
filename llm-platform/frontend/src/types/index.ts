// Common types for the LLM Platform

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  description?: string
  role: 'user' | 'admin'
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
  full_name?: string
  description?: string
  role?: 'user' | 'admin'
}

export interface UserUpdate {
  username?: string
  email?: string
  full_name?: string
  description?: string
  role?: 'user' | 'admin'
  is_active?: boolean
  password?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface ApiKey {
  id: number
  user_id: number
  name: string
  key_prefix: string
  is_active: boolean
  last_used_at?: string
  usage_count: number
  expires_at?: string
  created_at: string
}

export interface ApiKeyCreate {
  name: string
  expires_at?: string
}

export interface ApiKeyCreateResponse {
  api_key: ApiKey
  key: string
}

export interface Model {
  id: number
  name: string
  display_name: string
  provider: string
  endpoint_url?: string
  is_active: boolean
  priority: number
  max_tokens: number
  description?: string
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface ModelCreate {
  name: string
  display_name: string
  provider: string
  endpoint_url?: string
  is_active?: boolean
  priority?: number
  max_tokens?: number
  description?: string
  metadata?: Record<string, any>
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface ChatCompletionRequest {
  model: string
  messages: ChatMessage[]
  stream?: boolean
  temperature?: number
  max_tokens?: number
  top_p?: number
  frequency_penalty?: number
  presence_penalty?: number
  stop?: string | string[]
  user?: string
}

export interface ChatCompletionUsage {
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
}

export interface ChatCompletionChoice {
  index: number
  message: ChatMessage
  finish_reason?: string
}

export interface ChatCompletionResponse {
  id: string
  object: string
  created: number
  model: string
  choices: ChatCompletionChoice[]
  usage: ChatCompletionUsage
}

export interface AccessLog {
  id: number
  user_id: number
  model_id: number
  request_type: string
  status_code: number
  latency_ms: number
  total_tokens: number
  created_at: string
  error_message?: string
}

export interface OverviewStats {
  total_users: number
  active_users: number
  total_models: number
  active_models: number
  recent_api_calls_24h: number
  avg_latency_ms: number
}

export interface DailyStats {
  date: string
  request_count: number
  total_tokens: number
  avg_latency_ms: number
}

export interface UsageStats {
  period_days: number
  start_date: string
  end_date: string
  daily_stats: DailyStats[]
}