// Simple test to verify backend connection
const API_BASE_URL = 'http://localhost:8000'

async function testConnection() {
  console.log('🚀 Testing WealthOS Backend Connection...\n')
  
  try {
    // Test health check
    console.log('1. Testing health check...')
    const healthResponse = await fetch(`${API_BASE_URL}/health`)
    if (healthResponse.ok) {
      const healthData = await healthResponse.json()
      console.log('✅ Health check passed:', healthData)
    } else {
      console.log('❌ Health check failed:', healthResponse.status)
    }
    
    // Test anonymous user creation
    console.log('\n2. Testing anonymous user creation...')
    const userResponse = await fetch(`${API_BASE_URL}/users/anonymous`, {
      method: 'POST'
    })
    
    if (userResponse.ok) {
      const userData = await userResponse.json()
      console.log('✅ Anonymous user created:', userData)
      
      // Test login
      console.log('\n3. Testing anonymous user login...')
      const phonepart = userData.phone.slice(-8)
      const reversedPart = phonepart.split('').reverse().join('')
      const password = `Anon_${phonepart}_${reversedPart}!${userData.phone.length}`
      
      const formData = new URLSearchParams()
      formData.append('username', userData.phone)
      formData.append('password', password)
      
      const loginResponse = await fetch(`${API_BASE_URL}/users/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString()
      })
      
      if (loginResponse.ok) {
        const loginData = await loginResponse.json()
        console.log('✅ Login successful, token received')
        
        // Test chatbots
        console.log('\n4. Testing chatbots retrieval...')
        const chatbotsResponse = await fetch(`${API_BASE_URL}/chatbots`, {
          headers: {
            'Authorization': `Bearer ${loginData.access_token}`
          }
        })
        
        if (chatbotsResponse.ok) {
          const chatbots = await chatbotsResponse.json()
          console.log('✅ Chatbots retrieved:', chatbots.length, 'chatbots found')
          chatbots.forEach((bot, index) => {
            console.log(`   ${index + 1}. ${bot.name} (${bot.accessibility})`)
          })
        } else {
          console.log('❌ Chatbots retrieval failed:', chatbotsResponse.status)
        }
        
      } else {
        console.log('❌ Login failed:', loginResponse.status)
      }
      
    } else {
      console.log('❌ Anonymous user creation failed:', userResponse.status)
    }
    
  } catch (error) {
    console.error('❌ Connection failed:', error.message)
    console.log('\n💡 Make sure the backend is running on port 8000:')
    console.log('   cd backend && source .venv/bin/activate && python -m app.main')
  }
  
  console.log('\n🏁 Test completed!')
}

testConnection() 