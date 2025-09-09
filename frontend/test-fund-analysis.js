// Test the complete fund analysis flow
const API_BASE_URL = 'http://localhost:8000'

// Create a simple test image (base64 encoded PNG)
function createTestImage() {
  // Simple 1x1 pixel PNG in base64 (transparent)
  return 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAFCKjTEMwAAAABJRU5ErkJggg=='
}

async function testFundAnalysisFlow() {
  console.log('🚀 Testing Complete Fund Analysis Flow...\n')
  
  try {
    // Step 1: Create anonymous user
    console.log('1. Creating anonymous user...')
    const userResponse = await fetch(`${API_BASE_URL}/users/anonymous`, {
      method: 'POST'
    })
    
    if (!userResponse.ok) {
      throw new Error(`Failed to create anonymous user: ${userResponse.status}`)
    }
    
    const userData = await userResponse.json()
    console.log('✅ Anonymous user created:', userData.phone)
    
    // Step 2: Login
    console.log('\n2. Logging in...')
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
    
    if (!loginResponse.ok) {
      throw new Error(`Login failed: ${loginResponse.status}`)
    }
    
    const loginData = await loginResponse.json()
    const token = loginData.access_token
    console.log('✅ Login successful')
    
    // Step 3: Get chatbots
    console.log('\n3. Getting available chatbots...')
    const chatbotsResponse = await fetch(`${API_BASE_URL}/chatbots`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!chatbotsResponse.ok) {
      throw new Error(`Failed to get chatbots: ${chatbotsResponse.status}`)
    }
    
    const chatbots = await chatbotsResponse.json()
    console.log(`✅ Found ${chatbots.length} chatbots`)
    
    // Find the Image Analysis Bot specifically
    const imageChatbot = chatbots.find(bot => 
      bot.name.toLowerCase() === 'image analysis bot'
    ) || chatbots.find(bot => 
      bot.name.toLowerCase().includes('image analysis')
    ) || chatbots.find(bot => 
      bot.name.toLowerCase().includes('multimodal')
    ) || chatbots.find(bot => 
      bot.name.toLowerCase().includes('xiaomei')
    ) || chatbots[0]
    
    console.log(`   Using chatbot: ${imageChatbot.name}`)
    
    // Step 4: Start chat session
    console.log('\n4. Starting chat session...')
    const sessionResponse = await fetch(`${API_BASE_URL}/chatbots/${imageChatbot.id}/chat/start`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!sessionResponse.ok) {
      throw new Error(`Failed to start chat session: ${sessionResponse.status}`)
    }
    
    const sessionData = await sessionResponse.json()
    console.log('✅ Chat session started:', sessionData.id)
    
    // Step 5: Send image message
    console.log('\n5. Sending fund analysis image...')
    const imageData = createTestImage()
    
    const payload = {
      contents: [
        {
          content_type: 'text',
          content: '请分析这个基金投资组合截图，提供详细的分析和建议。Please analyze this fund portfolio screenshot.',
          order: 0
        },
        {
          content_type: 'image',
          content: imageData,
          meta_info: { filename: 'fund_portfolio.png' },
          order: 1
        }
      ]
    }
    
    const chatResponse = await fetch(`${API_BASE_URL}/chatbots/${imageChatbot.id}/chat/${sessionData.id}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
    
    if (!chatResponse.ok) {
      throw new Error(`Failed to send chat message: ${chatResponse.status}`)
    }
    
    console.log('✅ Image message sent successfully')
    
    // Step 6: Read streaming response
    console.log('\n6. Reading AI response...')
    if (chatResponse.body) {
      const reader = chatResponse.body.getReader()
      const decoder = new TextDecoder()
      let fullResponse = ''
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n').filter(line => line.trim())
        
        for (const line of lines) {
          try {
            const event = JSON.parse(line)
            if (event.type === 'text' && event.content) {
              fullResponse += event.content
              process.stdout.write(event.content) // Stream output in real-time
            }
          } catch (e) {
            // Ignore JSON parse errors for incomplete chunks
          }
        }
      }
      
      console.log('\n✅ AI analysis completed')
      console.log(`📝 Total response length: ${fullResponse.length} characters`)
    }
    
    // Step 7: Get chat history
    console.log('\n7. Retrieving chat history...')
    const historyResponse = await fetch(`${API_BASE_URL}/chatbots/${imageChatbot.id}/chat/${sessionData.id}/history`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (historyResponse.ok) {
      const history = await historyResponse.json()
      console.log(`✅ Chat history retrieved: ${history.length} messages`)
    } else {
      console.log('⚠️ Failed to retrieve chat history (non-critical)')
    }
    
    console.log('\n🎉 Fund Analysis Flow Test SUCCESSFUL! 🎉')
    console.log('\nNext steps:')
    console.log('- Open http://localhost:5173 in your browser')
    console.log('- Navigate to "AI Analysis" tab')
    console.log('- Upload a fund portfolio screenshot')
    console.log('- Watch the AI analyze your portfolio in real-time!')
    
  } catch (error) {
    console.error('\n❌ Test failed:', error.message)
    console.log('\nTroubleshooting:')
    console.log('1. Make sure backend is running: cd backend && source .venv/bin/activate && python -m app.main')
    console.log('2. Check that port 8000 is available')
    console.log('3. Verify database is accessible')
  }
}

// Run the test
testFundAnalysisFlow() 