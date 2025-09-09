// Quick test to check backend streaming behavior
const API_BASE_URL = 'http://localhost:8000'

async function testStreaming() {
  console.log('🧪 Testing backend streaming...')
  
  try {
    // Create anonymous user first
    const userResponse = await fetch(`${API_BASE_URL}/users/anonymous`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    const user = await userResponse.json()
    console.log('✅ Created user:', user.phone)

    // Login
    const phonepart = user.phone.slice(-8)
    const reversedPart = phonepart.split('').reverse().join('')
    const password = `Anon_${phonepart}_${reversedPart}!${user.phone.length}`
    
    const formData = new URLSearchParams()
    formData.append('username', user.phone)
    formData.append('password', password)

    const loginResponse = await fetch(`${API_BASE_URL}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString()
    })
    const { access_token } = await loginResponse.json()
    console.log('✅ Got auth token')

    // Get chatbots
    const botsResponse = await fetch(`${API_BASE_URL}/chatbots`, {
      headers: { 'Authorization': `Bearer ${access_token}` }
    })
    const bots = await botsResponse.json()
    const fundBot = bots.find(bot => bot.name.toLowerCase().includes('fund'))
    console.log('✅ Found fund bot:', fundBot?.name)

    // Start session
    const sessionResponse = await fetch(`${API_BASE_URL}/chatbots/${fundBot.id}/chat/start`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${access_token}` }
    })
    const session = await sessionResponse.json()
    console.log('✅ Started session:', session.id)

    // Send test message to check streaming
    console.log('🚀 Sending test message...')
    const payload = {
      contents: [{
        content_type: 'text',
        content: '你好，请简单介绍一下你自己',
        order: 0
      }]
    }

    const response = await fetch(`${API_BASE_URL}/chatbots/${fundBot.id}/chat/${session.id}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    console.log('📡 Response status:', response.status)
    console.log('📡 Response headers:', Object.fromEntries(response.headers.entries()))

    if (response.body) {
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let eventCount = 0
      let streamComplete = false
      
      console.log('📥 Starting to read stream...')
      
      const timeout = setTimeout(() => {
        if (!streamComplete) {
          console.log('⏰ Stream timeout after 30s')
          process.exit(1)
        }
      }, 30000)
      
      while (!streamComplete) {
        try {
          const { done, value } = await reader.read()
          if (done) {
            streamComplete = true
            break
          }
          
          const chunk = decoder.decode(value)
          const lines = chunk.split('\n').filter(line => line.trim())
          
          for (const line of lines) {
            try {
              const event = JSON.parse(line)
              eventCount++
              console.log(`📥 Event ${eventCount}:`, {
                type: event.type,
                content_length: event.content?.length || 0,
                message_type: event.message_type,
                has_metadata: !!event.metadata,
                final_response: event.metadata?.final_response
              })
              
              if (event.content) {
                console.log(`   Content preview: "${event.content.substring(0, 100)}${event.content.length > 100 ? '...' : ''}"`)
              }
            } catch (e) {
              console.error('❌ Failed to parse event:', line)
            }
          }
        } catch (e) {
          console.error('❌ Stream read error:', e)
          streamComplete = true
        }
      }
      
      clearTimeout(timeout)
      console.log(`✅ Stream complete! Received ${eventCount} events`)
    } else {
      console.log('❌ No response body')
    }

  } catch (error) {
    console.error('❌ Test failed:', error)
  }
}

testStreaming()