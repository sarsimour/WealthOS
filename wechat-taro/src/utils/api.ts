import Taro from '@tarojs/taro'

// API Configuration
const API_BASE_URL = 'http://localhost:8101/api'

// Types
export interface BitcoinPrice {
  identifier: string
  currency: string
  price: number
  timestamp: string
}

export interface HistoryDataPoint {
  timestamp: string
  price: number
  volume?: number
}

export interface ApiResponse<T> {
  data: T
  status: string
  message?: string
}

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

// Request wrapper with error handling
export const request = async <T>(options: {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
}): Promise<T> => {
  try {
    const response = await Taro.request({
      url: `${API_BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...options.header
      }
    })

    if (response.statusCode === 200) {
      return response.data as T
    } else {
      throw new Error(`HTTP Error: ${response.statusCode}`)
    }
  } catch (error) {
    console.error('API Request Error:', error)
    throw error
  }
}

// API Functions
export const api = {
  // 获取比特币当前价格
  getBitcoinPrice: (): Promise<BitcoinPrice> => {
    return request({
      url: '/v1/prices/crypto/btc?vs_currency=usd'
    })
  },

  // 获取比特币历史数据
  getBitcoinHistory: (period: string = '7d', currency: string = 'usd'): Promise<ApiResponse<HistoryDataPoint[]>> => {
    return request({
      url: `/v1/prices/bitcoin/history?period=${period}&currency=${currency}`
    })
  },

  // 获取比特币完整数据（当前价格+历史数据）
  getBitcoinFull: (days: number = 7, currency: string = 'usd'): Promise<ApiResponse<any>> => {
    return request({
      url: `/v1/prices/bitcoin/full?vs_currency=${currency}&days=${days}`
    })
  },

  // 健康检查
  healthCheck: (): Promise<{ status: string }> => {
    return request({
      url: '/health'
    })
  },

  // === User Management ===
  
  // 创建匿名用户
  createAnonymousUser: (): Promise<User> => {
    return request({
      url: '/v1/users/anonymous',
      method: 'POST'
    })
  },

  // 匿名用户登录
  loginAnonymousUser: async (phone: string): Promise<LoginResponse> => {
    // Generate password for anonymous user
    const phonepart = phone.slice(-8)
    const reversedPart = phonepart.split('').reverse().join('')
    const password = `Anon_${phonepart}_${reversedPart}!${phone.length}`
    
    const response = await Taro.request({
      url: `${API_BASE_URL}/v1/users/login`,
      method: 'POST',
      header: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      data: `username=${phone}&password=${password}`
    })
    
    if (response.statusCode === 200) {
      return response.data as LoginResponse
    } else {
      throw new Error(`Login failed: ${response.statusCode}`)
    }
  },

  // === Chatbot Management ===
  
  // 获取可用的聊天机器人
  getChatbots: (token: string): Promise<Chatbot[]> => {
    return request({
      url: '/v1/chatbots',
      header: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 开始聊天会话
  startChatSession: (chatbotId: string, token: string): Promise<ChatSession> => {
    return request({
      url: `/v1/chatbots/${chatbotId}/chat/start`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // === Chat Communication ===
  
  // 发送图片消息到聊天机器人
  sendImageToChatbot: async (
    chatbotId: string, 
    sessionId: string, 
    imagePath: string, 
    message: string, 
    token: string,
    onEvent?: (event: any) => void
  ): Promise<void> => {
    try {
      // Convert image to base64
      const fs = Taro.getFileSystemManager()
      const imageData = fs.readFileSync(imagePath, 'base64')
      
      // Send request with streaming response handling
      const response = await Taro.request({
        url: `${API_BASE_URL}/v1/chatbots/${chatbotId}/chat/${sessionId}`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        data: {
          contents: [
            {
              content_type: 'text',
              content: message,
              order: 0
            },
            {
              content_type: 'image',
              content: imageData,
              meta_info: { filename: 'portfolio.png' },
              order: 1
            }
          ]
        },
        responseType: 'text'
      })

      // Handle NDJSON streaming response
      if (response.statusCode === 200 && onEvent) {
        const responseText = response.data as string
        const lines = responseText.split('\n').filter(line => line.trim())
        
        for (const line of lines) {
          try {
            const event = JSON.parse(line)
            onEvent(event)
          } catch (e) {
            console.error('Failed to parse stream event:', e, 'Line:', line)
          }
        }
      }
    } catch (error) {
      console.error('Failed to send image to chatbot:', error)
      throw error
    }
  },

  // 获取聊天历史
  getChatHistory: (chatbotId: string, sessionId: string, token: string): Promise<any[]> => {
    return request({
      url: `/v1/chatbots/${chatbotId}/chat/${sessionId}/history`,
      header: {
        'Authorization': `Bearer ${token}`
      }
    })
  }
}

// Utility functions
export const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2
  }).format(price * 7.2) // Convert USD to CNY (approximate rate)
}

export const formatPercentage = (percentage: number): string => {
  const sign = percentage >= 0 ? '+' : ''
  return `${sign}${percentage.toFixed(2)}%`
}

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('zh-CN').format(num)
} 