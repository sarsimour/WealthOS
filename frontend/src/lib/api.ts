import { API_BASE_URL } from '../config/api'

// Types
export interface User {
  id: string
  phone: string
  email: string
  created_at: string
}

export interface Chatbot {
  id: string
  name: string
  description: string
  workflow_config_id: string
  accessibility: string
  avatar?: {
    inner_url: string
    public_url: string
  }
}

export interface ChatSession {
  id: string
  user_id: string
  chatbot_id: string
  created_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface MessageContent {
  content_type: 'text' | 'image' | 'audio' | 'video' | 'file' | 'image_url'
  content: string
  meta_info?: Record<string, string>
  order: number
  id: string
  message_id: string
}

export interface ChatMessage {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  timestamp: string
  contents: MessageContent[]
}

// Legacy interface for frontend compatibility
export interface FrontendMessage {
  id: string
  role: 'user' | 'assistant'
  type: 'text' | 'image' | 'image_url'
  content: string
  timestamp: Date
}

export interface StreamEvent {
  type: 'system_message' | 'tool_message' | 'ai_message' | 'text' | 'image' | 'analysis' | 'error'
  content?: string
  message_type?: 'system' | 'tool' | 'assistant' | 'unknown'
  url?: string
  result?: unknown
  message?: string
  timestamp?: string
  message_id?: string
  metadata?: {
    role?: string
    display?: boolean
    final_response?: boolean
    tool_call_id?: string
    original_type?: string
  }
}


export interface ChatHistoryMessage {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  contents: MessageContent[]
  created_at: string
}

// API Client Class
export class WealthOSAPI {
  private baseURL: string
  private token: string | null = null

  constructor() {
    this.baseURL = API_BASE_URL
  }

  // Helper method to make API calls
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {})
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        return await response.json()
      } else {
        return await response.text() as T
      }
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error)
      throw error
    }
  }

  // Set authentication token
  setToken(token: string) {
    this.token = token
  }

  // Get current token
  getToken(): string | null {
    return this.token
  }

  // === User Management ===

  async createAnonymousUser(): Promise<User> {
    return this.request<User>('/users/anonymous', {
      method: 'POST'
    })
  }

  async loginAnonymousUser(phone: string): Promise<LoginResponse> {
    // Generate password for anonymous user
    const phonepart = phone.slice(-8)
    const reversedPart = phonepart.split('').reverse().join('')
    const password = `Anon_${phonepart}_${reversedPart}!${phone.length}`
    
    const formData = new URLSearchParams()
    formData.append('username', phone)
    formData.append('password', password)

    return this.request<LoginResponse>('/users/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData.toString()
    })
  }

  // === Chatbot Management ===

  async getChatbots(): Promise<Chatbot[]> {
    return this.request<Chatbot[]>('/chatbots')
  }

  async startChatSession(chatbotId: string): Promise<ChatSession> {
    return this.request<ChatSession>(`/chatbots/${chatbotId}/chat/start`, {
      method: 'POST'
    })
  }

  // === Chat Communication ===

  async sendImageMessage(
    chatbotId: string,
    sessionId: string,
    imageFile: File,
    message: string,
    onEvent?: (event: StreamEvent) => void
  ): Promise<void> {
    try {
      // Convert image to base64
      const imageData = await this.fileToBase64(imageFile)
      
      const payload = {
        contents: [
          {
            content_type: 'text',
            content: message,
            order: 0
          },
          {
            content_type: 'image',
            content: imageData,
            meta_info: { filename: imageFile.name },
            order: 1
          }
        ]
      }

      const response = await fetch(`${this.baseURL}/chatbots/${chatbotId}/chat/${sessionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      // Handle streaming response
      if (onEvent && response.body) {
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          
          const chunk = decoder.decode(value)
          const lines = chunk.split('\n').filter(line => line.trim())
          
          for (const line of lines) {
            try {
              const event = JSON.parse(line) as StreamEvent
              onEvent(event)
            } catch (e) {
              console.error('Failed to parse stream event:', e, 'Raw line:', line)
            }
          }
        }
      }
    } catch (error) {
      console.error('Failed to send image message:', error)
      throw error
    }
  }

  async sendTextMessage(
    chatbotId: string,
    sessionId: string,
    message: string,
    onEvent?: (event: StreamEvent) => void
  ): Promise<void> {
    try {
      const payload = {
        contents: [
          {
            content_type: 'text',
            content: message,
            order: 0
          }
        ]
      }

      const response = await fetch(`${this.baseURL}/chatbots/${chatbotId}/chat/${sessionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      // Handle streaming response
      if (onEvent && response.body) {
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          
          const chunk = decoder.decode(value)
          const lines = chunk.split('\n').filter(line => line.trim())
          
          for (const line of lines) {
            try {
              const event = JSON.parse(line) as StreamEvent
              onEvent(event)
            } catch (e) {
              console.error('Failed to parse stream event:', e, 'Raw line:', line)
            }
          }
        }
      }
    } catch (error) {
      console.error('Failed to send text message:', error)
      throw error
    }
  }

  async getChatHistory(chatbotId: string, sessionId: string): Promise<ChatHistoryMessage[]> {
    return this.request<ChatHistoryMessage[]>(`/chatbots/${chatbotId}/chat/${sessionId}/history`)
  }

  // === Health Checks ===

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health')
  }

  async imageAnalysisHealthCheck(): Promise<{ status: string }> {
    // This endpoint doesn't exist in the current backend
    // Return the main health check instead
    return this.healthCheck()
  }

  // === Utility Methods ===

  private async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        if (typeof reader.result === 'string') {
          // Remove data URL prefix to get just the base64 data
          const base64 = reader.result.split(',')[1]
          resolve(base64)
        } else {
          reject(new Error('Failed to convert file to base64'))
        }
      }
      reader.onerror = () => reject(new Error('File reading failed'))
      reader.readAsDataURL(file)
    })
  }
}

// Export singleton instance
export const api = new WealthOSAPI() 