import { api } from '../lib/api'

export const testBackendConnection = async (): Promise<{
  success: boolean
  message: string
  details?: unknown
}> => {
  try {
    console.log('🔍 Testing backend connection...')
    
    // Test basic health check
    const health = await api.healthCheck()
    console.log('✅ Basic health check passed:', health)
    
    // Test image analysis health check
    const imageHealth = await api.imageAnalysisHealthCheck()
    console.log('✅ Image analysis health check passed:', imageHealth)
    
    // Test creating anonymous user
    const user = await api.createAnonymousUser()
    console.log('✅ Anonymous user creation passed:', user)
    
    // Test login
    const loginResponse = await api.loginAnonymousUser(user.phone)
    console.log('✅ Anonymous user login passed:', loginResponse)
    
    // Set token and test chatbots
    api.setToken(loginResponse.access_token)
    const chatbots = await api.getChatbots()
    console.log('✅ Chatbots fetch passed:', chatbots)
    
    return {
      success: true,
      message: 'All backend connection tests passed successfully!',
      details: {
        health,
        imageHealth,
        user: { id: user.id, phone: user.phone },
        chatbotsCount: chatbots.length
      }
    }
  } catch (error) {
    console.error('❌ Backend connection test failed:', error)
    return {
      success: false,
      message: `Backend connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      details: error
    }
  }
}