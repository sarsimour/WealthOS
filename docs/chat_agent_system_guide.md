# WealthOS Chat & Agent System Integration Guide

This document provides a complete reference for integrating with the WealthOS chat and agent system from the WeChat-taro frontend.

## System Architecture Overview

The WealthOS backend uses a 3-level agent architecture:

1. **LLM Model Config** - Base API configurations for different AI providers
2. **Agent Config** - Specific agent personalities and capabilities  
3. **Workflow Config** - Orchestrates multiple agents in complex workflows

## Database Models

### 1. LLM Model Configuration

```sql
-- Table: llm_model_configs
{
  "id": "UUID",
  "name": "string (unique)",
  "provider": "gemini|openai|qwen",
  "model_name": "gemini-pro|gpt-4-turbo|etc",
  "api_key_env": "GEMINI_API_KEY",
  "base_url_env": "QWEN_BASE_URL (optional)",
  "temperature": 0.7,
  "max_tokens": 1500,
  "multimodal": boolean,
  "function_calling": boolean,
  "streaming": boolean,
  "config": {}, // Additional JSON config
  "is_active": boolean
}
```

### 2. Agent Configuration

```sql
-- Table: agent_configs
{
  "id": "UUID",
  "name": "string (unique)",
  "agent_type": "character|analyzer|summarizer",
  "description": "text",
  "llm_model_config_id": "UUID (FK)",
  "personality": {}, // JSON
  "memory_config": {}, // JSON
  "background": {}, // JSON
  "principles": [], // JSON array
  "character_features": {}, // JSON
  "tone_style": {}, // JSON
  "talking_style": {}, // JSON
  "body_states": {}, // JSON
  "default_state": "string",
  "config": {}, // Additional JSON config
  "is_active": boolean
}
```

### 3. Workflow Configuration

```sql
-- Table: workflow_configs
{
  "id": "UUID",
  "name": "string (unique)",
  "workflow_type": "fund_analysis|image_analysis|basic_chat",
  "workflow_template_name": "BasicChatWorkflow|CompanionWorkflow|etc",
  "description": "text",
  "config": {}, // JSON
  "version": "1.0",
  "is_active": boolean
}
```

### 4. Workflow Agent Assignment

```sql
-- Table: workflow_agent_assignments
{
  "id": "UUID",
  "workflow_config_id": "UUID (FK)",
  "agent_config_id": "UUID (FK)",
  "node_name": "analyzer|summarizer|responder",
  "node_description": "text",
  "node_position": {}, // JSON for graph position
  "override_config": {}, // JSON node-specific overrides
  "is_active": boolean
}
```

### 5. Chatbot Configuration

```sql
-- Table: chatbots
{
  "id": "UUID",
  "name": "string",
  "avatar": "string (URL)",
  "description": "text",
  "workflow_config_id": "UUID (FK)",
  "voice_model_id": "UUID",
  "video_model_id": "UUID",
  "org_id": "UUID (FK)",
  "creator_id": "UUID (FK)",
  "accessibility": "secret|org|public",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

## API Endpoints for WeChat-taro

### 1. User Management

```typescript
// Create anonymous user (for WeChat-taro)
POST /api/v1/users/anonymous
Response: {
  "id": "UUID",
  "phone": "anonymous_12345678",
  "email": "anonymous_12345678@example.com",
  "created_at": "timestamp"
}

// Login with anonymous user
POST /api/v1/users/login
Content-Type: application/x-www-form-urlencoded
Body: {
  username: "anonymous_12345678",
  password: "Anon_12345678_87654321!17" // Auto-generated
}
Response: {
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

### 2. Get Available Chatbots

```typescript
GET /api/v1/chatbots
Headers: { Authorization: "Bearer <token>" }
Response: [
  {
    "id": "UUID",
    "name": "Fund Analysis Bot",
    "description": "AI assistant for fund portfolio analysis",
    "workflow_config_id": "UUID",
    "accessibility": "public",
    "avatar": {
      "inner_url": "string",
      "public_url": "string"
    }
  }
]
```

### 3. Chat Session Management

```typescript
// Start chat session
POST /api/v1/chatbots/{chatbot_id}/chat/start
Headers: { Authorization: "Bearer <token>" }
Response: {
  "id": "UUID",
  "user_id": "UUID",
  "chatbot_id": "UUID",
  "created_at": "timestamp"
}

// Send message with image (multipart form)
POST /api/v1/chatbots/{chatbot_id}/chat/{session_id}
Headers: { 
  Authorization: "Bearer <token>",
  Content-Type: "multipart/form-data"
}
Body (FormData): {
  message: "Please analyze this fund portfolio",
  image: File // Image file
}

// Or send JSON message
POST /api/v1/chatbots/{chatbot_id}/chat/{session_id}
Headers: { 
  Authorization: "Bearer <token>",
  Content-Type: "application/json"
}
Body: {
  "contents": [
    {
      "content_type": "text",
      "content": "Please analyze this portfolio",
      "order": 0
    },
    {
      "content_type": "image",
      "content": "base64_encoded_image_data",
      "meta_info": {"filename": "portfolio.png"},
      "order": 1
    }
  ]
}

// Response: Streaming NDJSON
Content-Type: application/x-ndjson
// Stream of events:
{"type": "text", "content": "I can see your portfolio...", "message_id": "UUID"}
{"type": "image", "url": "https://...", "message_id": "UUID"}
{"type": "error", "message": "Error description"}
```

### 4. Chat History

```typescript
GET /api/v1/chatbots/{chatbot_id}/chat/{session_id}/history?limit=20&offset=0
Headers: { Authorization: "Bearer <token>" }
Response: [
  {
    "id": "UUID",
    "session_id": "UUID",
    "role": "user|assistant",
    "contents": [
      {
        "content_type": "text|image|image_url",
        "content": "string|base64|url",
        "order": 0,
        "meta_info": {}
      }
    ],
    "created_at": "timestamp"
  }
]
```

## WeChat-taro Implementation Plan

### 1. Create Fund Analysis Page

```typescript
// File: wechat-taro/src/pages/fund-analysis/index.tsx
import React, { useState, useEffect } from 'react'
import { View, Text, Image, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { api } from '../../utils/api'

interface FundAnalysisState {
  user: any | null
  chatbot: any | null
  session: any | null
  messages: any[]
  loading: boolean
}

const FundAnalysis: React.FC = () => {
  const [state, setState] = useState<FundAnalysisState>({
    user: null,
    chatbot: null,
    session: null,
    messages: [],
    loading: false
  })

  // Initialize anonymous user and get image analysis chatbot
  useEffect(() => {
    initializeFundAnalysis()
  }, [])

  const initializeFundAnalysis = async () => {
    try {
      setState(prev => ({ ...prev, loading: true }))
      
      // Create anonymous user
      const user = await api.createAnonymousUser()
      
      // Login and get token
      const loginResponse = await api.loginAnonymousUser(user.phone)
      
      // Store token for future requests
      Taro.setStorageSync('auth_token', loginResponse.access_token)
      
      // Get available chatbots and find image analysis one
      const chatbots = await api.getChatbots(loginResponse.access_token)
      const imageChatbot = chatbots.find(bot => 
        bot.name.includes('Image') || bot.workflow_type === 'image_analysis'
      )
      
      if (imageChatbot) {
        // Start chat session
        const session = await api.startChatSession(
          imageChatbot.id, 
          loginResponse.access_token
        )
        
        setState(prev => ({
          ...prev,
          user,
          chatbot: imageChatbot,
          session,
          loading: false
        }))
      }
    } catch (error) {
      console.error('Failed to initialize fund analysis:', error)
      setState(prev => ({ ...prev, loading: false }))
    }
  }

  const uploadScreenshot = () => {
    Taro.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: async (res) => {
        const tempFilePath = res.tempFilePaths[0]
        await sendImageMessage(tempFilePath)
      }
    })
  }

  const sendImageMessage = async (imagePath: string) => {
    try {
      setState(prev => ({ ...prev, loading: true }))
      
      const token = Taro.getStorageSync('auth_token')
      
      // Send image with message to chatbot
      const response = await api.sendImageToChatbot(
        state.chatbot.id,
        state.session.id,
        imagePath,
        "Please analyze this fund portfolio screenshot",
        token
      )
      
      // Handle streaming response
      await handleStreamingResponse(response)
      
    } catch (error) {
      console.error('Failed to send image:', error)
    } finally {
      setState(prev => ({ ...prev, loading: false }))
    }
  }

  const handleStreamingResponse = async (response: any) => {
    // Handle NDJSON streaming response
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      const chunk = decoder.decode(value)
      const lines = chunk.split('\n').filter(line => line.trim())
      
      for (const line of lines) {
        try {
          const event = JSON.parse(line)
          handleChatEvent(event)
        } catch (e) {
          console.error('Failed to parse stream event:', e)
        }
      }
    }
  }

  const handleChatEvent = (event: any) => {
    setState(prev => {
      const newMessages = [...prev.messages]
      
      if (event.type === 'text') {
        newMessages.push({
          id: event.message_id,
          role: 'assistant',
          type: 'text',
          content: event.content,
          timestamp: new Date()
        })
      } else if (event.type === 'image') {
        newMessages.push({
          id: event.message_id,
          role: 'assistant',
          type: 'image',
          content: event.url,
          timestamp: new Date()
        })
      } else if (event.type === 'error') {
        console.error('Chat error:', event.message)
      }
      
      return { ...prev, messages: newMessages }
    })
  }

  return (
    <View className='fund-analysis-page'>
      <View className='header'>
        <Text className='title'>基金分析</Text>
      </View>
      
      {state.loading && (
        <View className='loading'>
          <Text>处理中...</Text>
        </View>
      )}
      
      <View className='upload-section'>
        <Button onClick={uploadScreenshot} disabled={!state.session}>
          上传基金截图
        </Button>
      </View>
      
      <View className='chat-messages'>
        {state.messages.map((message, index) => (
          <View key={index} className={`message ${message.role}`}>
            {message.type === 'text' && (
              <Text className='message-text'>{message.content}</Text>
            )}
            {message.type === 'image' && (
              <Image src={message.content} className='message-image' />
            )}
          </View>
        ))}
      </View>
    </View>
  )
}

export default FundAnalysis
```

### 2. Update API Utils

```typescript
// File: wechat-taro/src/utils/api.ts
// Add these methods to existing API class

class API {
  // ... existing methods ...

  // User management
  async createAnonymousUser() {
    const response = await Taro.request({
      url: `${API_BASE_URL}/v1/users/anonymous`,
      method: 'POST'
    })
    return response.data
  }

  async loginAnonymousUser(phone: string) {
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
    return response.data
  }

  // Chatbot management
  async getChatbots(token: string) {
    const response = await Taro.request({
      url: `${API_BASE_URL}/v1/chatbots`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      }
    })
    return response.data
  }

  async startChatSession(chatbotId: string, token: string) {
    const response = await Taro.request({
      url: `${API_BASE_URL}/v1/chatbots/${chatbotId}/chat/start`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${token}`
      }
    })
    return response.data
  }

  async sendImageToChatbot(
    chatbotId: string, 
    sessionId: string, 
    imagePath: string, 
    message: string, 
    token: string
  ) {
    // Convert image to base64
    const fs = Taro.getFileSystemManager()
    const imageData = fs.readFileSync(imagePath, 'base64')
    
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
      }
    })
    return response.data
  }

  async getChatHistory(chatbotId: string, sessionId: string, token: string) {
    const response = await Taro.request({
      url: `${API_BASE_URL}/v1/chatbots/${chatbotId}/chat/${sessionId}/history`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      }
    })
    return response.data
  }
}

export const api = new API()
```

### 3. Update App Configuration

```typescript
// File: wechat-taro/src/app.config.ts
export default defineAppConfig({
  pages: [
    'pages/index/index',
    'pages/market/index',
    'pages/portfolio/index',
    'pages/fund-analysis/index', // Add fund analysis page
    'pages/profile/index'
  ],
  // ... rest of config
  tabBar: {
    // ... existing config
    list: [
      {
        pagePath: 'pages/index/index',
        text: '首页'
      },
      {
        pagePath: 'pages/market/index',
        text: '行情'
      },
      {
        pagePath: 'pages/portfolio/index',
        text: '组合'
      },
      {
        pagePath: 'pages/fund-analysis/index',
        text: '基金分析'
      },
      {
        pagePath: 'pages/profile/index',
        text: '我的'
      }
    ]
  }
})
```

## Key Features Implemented

1. **Anonymous User Creation**: Automatically creates temporary users for WeChat mini-program
2. **Image Upload & Analysis**: Supports both camera and album image selection
3. **Streaming Chat Response**: Real-time processing of AI responses
4. **Multi-modal Messages**: Handles text, images, and generated content
5. **Session Management**: Maintains chat context across interactions
6. **Error Handling**: Robust error handling for network and API failures

## Security Considerations

1. **Anonymous Users**: Have limited access and expire after 7 days
2. **Token Management**: JWT tokens stored securely in Taro storage
3. **Public Chatbots**: Only public accessibility chatbots are accessible to anonymous users
4. **Rate Limiting**: Backend implements rate limiting on API endpoints

## Testing & Debugging

1. **Backend Health Check**: `GET /api/v1/wealthos/health`
2. **Database Verification**: Check that image analysis chatbots exist
3. **Token Validation**: Ensure JWT tokens are valid for API access
4. **Streaming Response**: Test NDJSON parsing in WeChat devtools
