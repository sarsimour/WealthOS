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