export interface Message {
    id: string
    text: string
    timestamp: Date
    prediction?: 'ham' | 'spam'
    confidence?: number
  }
  
  export interface ClassificationHistory {
    id: string
    message: string
    prediction: 'ham' | 'spam'
    confidence: number
    timestamp: Date
  }
  
  export type Theme = 'light' | 'dark' | 'system'
  
  export interface User {
    id: string
    name: string
    email: string
  }
  
  export interface ApiError {
    error: string
    detail?: string
    timestamp: string
  }