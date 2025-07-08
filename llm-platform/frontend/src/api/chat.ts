import api from './index'
import type { ChatCompletionRequest, ChatCompletionResponse } from '@/types'

export const chatApi = {
  // Create chat completion
  createChatCompletion(data: ChatCompletionRequest): Promise<ChatCompletionResponse> {
    return api.post('/chat/completions', data).then(res => res.data)
  },
  
  // Create streaming chat completion
  createStreamingChatCompletion(data: ChatCompletionRequest): Promise<ReadableStream> {
    return fetch('/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
      },
      body: JSON.stringify({ ...data, stream: true })
    }).then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return response.body!
    })
  }
}