/**
 * API Configuration
 * Easy switching between mock and real backend
 */

export const API_CONFIG = {
  // 🎭 MOCK API - Use this for testing frontend without backend dependencies
  MOCK: {
    BASE_URL: 'http://localhost:8002/api/v1',
    DESCRIPTION: 'Mock API with fake data for testing'
  },
  
  // 🔗 REAL API - Use this for production with actual data providers
  REAL: {
    BASE_URL: 'http://localhost:8000', 
    DESCRIPTION: 'Real WealthOS backend with chat and image analysis'
  }
} as const

// 🚀 CURRENT CONFIGURATION - Change this to switch between APIs
// Set to 'MOCK' for testing, 'REAL' for production
type ApiMode = 'MOCK' | 'REAL'
export const CURRENT_MODE: ApiMode = 'REAL'

// Export the current API base URL
export const API_BASE_URL = API_CONFIG[CURRENT_MODE].BASE_URL

// Helper functions
export const getCurrentApiInfo = () => ({
  mode: CURRENT_MODE,
  url: API_BASE_URL,
  description: API_CONFIG[CURRENT_MODE].DESCRIPTION
})

export const isMockMode = (): boolean => CURRENT_MODE.includes('MOCK')
export const isRealMode = (): boolean => CURRENT_MODE.includes('REAL') 