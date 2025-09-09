// Simple test script to verify backend APIs
// Run this with: node test-backend.js

const API_BASE_URL = 'http://localhost:8101/api'

async function testAPI(endpoint, options = {}) {
  try {
    const url = `${API_BASE_URL}${endpoint}`
    console.log(`Testing: ${url}`)
    
    const response = await fetch(url, {
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      body: options.body ? JSON.stringify(options.body) : undefined
    })
    
    const data = await response.text()
    console.log(`Response [${response.status}]:`, data.length > 200 ? data.substring(0, 200) + '...' : data)
    return { status: response.status, data }
  } catch (error) {
    console.error(`Error testing ${endpoint}:`, error.message)
    return { error: error.message }
  }
}

async function runTests() {
  console.log('🚀 Testing WealthOS Backend APIs...\n')
  
  // Test 1: Health check
  console.log('1. Health Check')
  await testAPI('/health')
  console.log()
  
  // Test 2: Create anonymous user
  console.log('2. Create Anonymous User')
  const userResult = await testAPI('/v1/users/anonymous', { method: 'POST' })
  let user = null
  try {
    user = JSON.parse(userResult.data)
  } catch (e) {
    console.log('Failed to parse user data')
  }
  console.log()
  
  if (user && user.phone) {
    // Test 3: Login anonymous user
    console.log('3. Login Anonymous User')
    const phonepart = user.phone.slice(-8)
    const reversedPart = phonepart.split('').reverse().join('')
    const password = `Anon_${phonepart}_${reversedPart}!${user.phone.length}`
    
    const loginResult = await testAPI('/v1/users/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: `username=${user.phone}&password=${password}`
    })
    
    let token = null
    try {
      const loginData = JSON.parse(loginResult.data)
      token = loginData.access_token
    } catch (e) {
      console.log('Failed to parse login data')
    }
    console.log()
    
    if (token) {
      // Test 4: Get chatbots
      console.log('4. Get Chatbots')
      await testAPI('/v1/chatbots', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      console.log()
      
      // Test 5: Image analysis health check
      console.log('5. Image Analysis Health Check')
      await testAPI('/v1/wealthos/health')
      console.log()
    }
  }
  
  console.log('✅ Backend API tests completed!')
}

// Check if fetch is available (Node.js 18+)
if (typeof fetch === 'undefined') {
  console.log('❌ This script requires Node.js 18+ with fetch support')
  console.log('Or install node-fetch: npm install node-fetch')
  process.exit(1)
}

runTests().catch(console.error) 