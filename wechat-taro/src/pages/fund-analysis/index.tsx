import React, { useState, useEffect } from 'react'
import { View, Text, Image, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { api } from '../../utils/api'
import './index.scss'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  type: 'text' | 'image'
  content: string
  timestamp: Date
}

interface FundAnalysisState {
  user: any | null
  chatbot: any | null
  session: any | null
  messages: ChatMessage[]
  loading: boolean
  initializing: boolean
}

const FundAnalysis: React.FC = () => {
  const [state, setState] = useState<FundAnalysisState>({
    user: null,
    chatbot: null,
    session: null,
    messages: [],
    loading: false,
    initializing: true
  })

  // Initialize anonymous user and get image analysis chatbot
  useEffect(() => {
    initializeFundAnalysis()
  }, [])

  const initializeFundAnalysis = async () => {
    try {
      setState(prev => ({ ...prev, initializing: true }))
      
      // Check if we already have a token
      let token = Taro.getStorageSync('auth_token')
      let user = Taro.getStorageSync('current_user')
      
      if (!token || !user) {
        // Create anonymous user
        user = await api.createAnonymousUser()
        console.log('Created anonymous user:', user)
        
        // Login and get token
        const loginResponse = await api.loginAnonymousUser(user.phone)
        token = loginResponse.access_token
        
        // Store for future use
        Taro.setStorageSync('auth_token', token)
        Taro.setStorageSync('current_user', user)
      }
      
      // Get available chatbots and find image analysis one
      const chatbots = await api.getChatbots(token)
      console.log('Available chatbots:', chatbots)
      
      // Look for image analysis or fund analysis chatbot
      const imageChatbot = chatbots.find(bot => 
        bot.name.toLowerCase().includes('image') || 
        bot.name.toLowerCase().includes('fund') ||
        bot.name.toLowerCase().includes('analysis')
      ) || chatbots[0] // Fallback to first available chatbot
      
      if (imageChatbot) {
        // Start chat session
        const session = await api.startChatSession(imageChatbot.id, token)
        console.log('Started chat session:', session)
        
        setState(prev => ({
          ...prev,
          user,
          chatbot: imageChatbot,
          session,
          initializing: false
        }))
      } else {
        console.error('No suitable chatbot found')
        Taro.showToast({
          title: '没有找到可用的分析机器人',
          icon: 'none'
        })
        setState(prev => ({ ...prev, initializing: false }))
      }
    } catch (error) {
      console.error('Failed to initialize fund analysis:', error)
      Taro.showToast({
        title: '初始化失败，请重试',
        icon: 'none'
      })
      setState(prev => ({ ...prev, initializing: false }))
    }
  }

  const uploadScreenshot = () => {
    if (!state.session) {
      Taro.showToast({
        title: '正在初始化，请稍候',
        icon: 'none'
      })
      return
    }

    Taro.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: async (res) => {
        const tempFilePath = res.tempFilePaths[0]
        await sendImageMessage(tempFilePath)
      },
      fail: (error) => {
        console.error('Failed to choose image:', error)
        Taro.showToast({
          title: '选择图片失败',
          icon: 'none'
        })
      }
    })
  }

  const sendImageMessage = async (imagePath: string) => {
    try {
      setState(prev => ({ ...prev, loading: true }))
      
      // Add user message to chat
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        type: 'image',
        content: imagePath,
        timestamp: new Date()
      }
      
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, userMessage]
      }))
      
      const token = Taro.getStorageSync('auth_token')
      
      // Send image with message to chatbot
      await api.sendImageToChatbot(
        state.chatbot.id,
        state.session.id,
        imagePath,
        "请分析这个基金投资组合截图，提供详细的分析和建议",
        token,
        (event) => handleChatEvent(event)
      )
      
    } catch (error) {
      console.error('Failed to send image:', error)
      Taro.showToast({
        title: '发送失败，请重试',
        icon: 'none'
      })
    } finally {
      setState(prev => ({ ...prev, loading: false }))
    }
  }

  const handleChatEvent = (event: any) => {
    console.log('Received chat event:', event)
    
    setState(prev => {
      const newMessages = [...prev.messages]
      
      if (event.type === 'text') {
        // Check if we already have a message with this ID
        const existingIndex = newMessages.findIndex(msg => msg.id === event.message_id)
        
        if (existingIndex >= 0) {
          // Update existing message
          newMessages[existingIndex] = {
            ...newMessages[existingIndex],
            content: newMessages[existingIndex].content + event.content
          }
        } else {
          // Add new message
          newMessages.push({
            id: event.message_id || Date.now().toString(),
            role: 'assistant',
            type: 'text',
            content: event.content,
            timestamp: new Date()
          })
        }
      } else if (event.type === 'image') {
        newMessages.push({
          id: event.message_id || Date.now().toString(),
          role: 'assistant',
          type: 'image',
          content: event.url,
          timestamp: new Date()
        })
      } else if (event.type === 'error') {
        console.error('Chat error:', event.message)
        Taro.showToast({
          title: '分析出错，请重试',
          icon: 'none'
        })
      }
      
      return { ...prev, messages: newMessages }
    })
  }

  const clearChat = () => {
    setState(prev => ({
      ...prev,
      messages: []
    }))
  }

  if (state.initializing) {
    return (
      <View className='fund-analysis-page'>
        <View className='loading-container'>
          <Text className='loading-text'>正在初始化分析系统...</Text>
        </View>
      </View>
    )
  }

  return (
    <View className='fund-analysis-page'>
      <View className='header'>
        <Text className='title'>基金分析助手</Text>
        {state.chatbot && (
          <Text className='subtitle'>使用 {state.chatbot.name}</Text>
        )}
      </View>
      
      <View className='upload-section'>
        <Button 
          className='upload-btn'
          onClick={uploadScreenshot} 
          disabled={!state.session || state.loading}
          loading={state.loading}
        >
          {state.loading ? '分析中...' : '上传基金截图'}
        </Button>
        <Text className='upload-tip'>
          支持支付宝、银行APP等基金持仓截图
        </Text>
      </View>
      
      <View className='chat-container'>
        {state.messages.length === 0 ? (
          <View className='empty-state'>
            <Text className='empty-icon'>📊</Text>
            <Text className='empty-title'>欢迎使用基金分析助手</Text>
            <Text className='empty-desc'>
              上传您的基金投资组合截图，我将为您提供专业的分析和建议
            </Text>
          </View>
        ) : (
          <View className='chat-messages'>
            {state.messages.map((message, index) => (
              <View key={index} className={`message ${message.role}`}>
                <View className='message-content'>
                  {message.type === 'text' && (
                    <Text className='message-text'>{message.content}</Text>
                  )}
                  {message.type === 'image' && (
                    <Image 
                      src={message.content} 
                      className='message-image'
                      mode='aspectFit'
                    />
                  )}
                </View>
                <Text className='message-time'>
                  {message.timestamp.toLocaleTimeString()}
                </Text>
              </View>
            ))}
            
            {state.loading && (
              <View className='message assistant'>
                <View className='message-content'>
                  <Text className='typing-indicator'>AI正在分析中...</Text>
                </View>
              </View>
            )}
          </View>
        )}
      </View>
      
      {state.messages.length > 0 && (
        <View className='chat-actions'>
          <Button 
            className='clear-btn'
            size='mini'
            onClick={clearChat}
          >
            清空对话
          </Button>
        </View>
      )}
    </View>
  )
}

export default FundAnalysis 