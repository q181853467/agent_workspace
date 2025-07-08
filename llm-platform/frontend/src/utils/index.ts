import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

// Extend dayjs with plugins
dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

// Format timestamp
export const formatTime = (timestamp: string | Date, format = 'YYYY-MM-DD HH:mm:ss') => {
  return dayjs(timestamp).format(format)
}

// Format relative time
export const formatRelativeTime = (timestamp: string | Date) => {
  return dayjs(timestamp).fromNow()
}

// Format file size
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Format number with commas
export const formatNumber = (num: number): string => {
  return num.toLocaleString()
}

// Truncate text
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

// Generate random ID
export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9)
}

// Debounce function
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void => {
  let timeout: NodeJS.Timeout
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

// Throttle function
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void => {
  let inThrottle: boolean
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => inThrottle = false, wait)
    }
  }
}

// Deep clone object
export const deepClone = <T>(obj: T): T => {
  return JSON.parse(JSON.stringify(obj))
}

// Check if value is empty
export const isEmpty = (value: any): boolean => {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

// Validate email
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// Validate URL
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

// Copy to clipboard
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (error) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    
    try {
      document.execCommand('copy')
      document.body.removeChild(textArea)
      return true
    } catch (err) {
      document.body.removeChild(textArea)
      return false
    }
  }
}

// Download file
export const downloadFile = (data: BlobPart, filename: string, type = 'text/plain') => {
  const file = new Blob([data], { type })
  const url = URL.createObjectURL(file)
  const link = document.createElement('a')
  
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// Get status color
export const getStatusColor = (status: string): string => {
  const statusColors: Record<string, string> = {
    active: 'success',
    inactive: 'danger',
    pending: 'warning',
    error: 'danger',
    success: 'success',
    warning: 'warning',
    info: 'info'
  }
  
  return statusColors[status.toLowerCase()] || 'info'
}

// Get provider icon
export const getProviderIcon = (provider: string): string => {
  const providerIcons: Record<string, string> = {
    openai: '🤖',
    deepseek: '🧠',
    anthropic: '🎭',
    google: '🔍',
    meta: '📘',
    microsoft: '🏢'
  }
  
  return providerIcons[provider.toLowerCase()] || '⚡'
}