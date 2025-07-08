import api from './index'
import type { LoginRequest, Token, User, UserCreate } from '@/types'

export const authApi = {
  // User login
  login(data: LoginRequest): Promise<Token> {
    return api.post('/auth/login', data).then(res => res.data)
  },
  
  // User registration
  register(data: UserCreate): Promise<User> {
    return api.post('/auth/register', data).then(res => res.data)
  },
  
  // Get current user info
  getCurrentUser(): Promise<User> {
    return api.get('/users/me').then(res => res.data)
  }
}