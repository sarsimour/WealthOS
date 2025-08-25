import React, { useState, useEffect, useCallback } from 'react'
import { Loader2, AlertCircle } from 'lucide-react'
import { api, type User, type Chatbot, type ChatSession, type StreamEvent, type FrontendMessage } from '../lib/api'
import ImageUpload from './ImageUpload'
import AnalysisResult from './AnalysisResult'

interface FundAnalysisState {
  user: User | null
  chatbot: Chatbot | null
  session: ChatSession | null
  messages: FrontendMessage[]
  loading: boolean
  initializing: boolean
  error: string | null
  isStreaming: boolean
  uploadedImage: string | null
}

const FundAnalysis: React.FC = () => {
  const [state, setState] = useState<FundAnalysisState>({
    user: null,
    chatbot: null,
    session: null,
    messages: [],
    loading: false,
    initializing: true,
    error: null,
    isStreaming: false,
    uploadedImage: null
  })


  // Initialize anonymous user and chatbot session
  const initializeFundAnalysis = useCallback(async (): Promise<void> => {
    try {
      setState(prev => ({ ...prev, initializing: true, error: null }))
      
      // Check if we have stored auth data
      let user = null
      let token = api.getToken()
      
      // Try to get user from localStorage
      const storedUser = localStorage.getItem('current_user')
      if (storedUser) {
        try {
          user = JSON.parse(storedUser)
        } catch {
          console.error('Failed to parse stored user data')
        }
      }
      
      if (!token || !user) {
        // Create anonymous user
        user = await api.createAnonymousUser()
        console.log('Created anonymous user:', user)
        
        // Login and get token
        const loginResponse = await api.loginAnonymousUser(user.phone)
        token = loginResponse.access_token
        
        // Set token in API client
        api.setToken(token)
        
        // Store in localStorage
        localStorage.setItem('auth_token', token)
        localStorage.setItem('current_user', JSON.stringify(user))
      }
      
      // Get available chatbots
      const chatbots = await api.getChatbots()
      console.log('Available chatbots:', chatbots)
      
      // Find the best chatbot for fund holdings image analysis
      console.log('Available chatbots:', chatbots.map(bot => ({ name: bot.name, id: bot.id })))
      
      const imageChatbot =
        chatbots.find(bot => bot.name.trim().toLowerCase() === 'fund portfolio advisor v2') ||
        chatbots[0] // Fallback to first available
      
      console.log('Selected chatbot for image analysis:', imageChatbot?.name, imageChatbot?.id)
      
      if (imageChatbot) {
        // Start chat session
        const session = await api.startChatSession(imageChatbot.id)
        console.log('Started chat session:', session)
        
        setState(prev => ({
          ...prev,
          user,
          chatbot: imageChatbot,
          session,
          initializing: false
        }))
      } else {
        throw new Error('No suitable chatbot found for fund analysis')
      }
    } catch (error) {
      console.error('Failed to initialize fund analysis:', error)
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to initialize fund analysis',
        initializing: false
      }))
    }
  }, [])

    useEffect(() => {
    // Load stored auth data
    const storedToken = localStorage.getItem('auth_token')
    
    if (storedToken) {
      api.setToken(storedToken)
    }
    
    initializeFundAnalysis()
  }, [initializeFundAnalysis])

  const handleChatEvent = useCallback((event: StreamEvent) => {
    console.log('📥 Received event:', event)
    
    try {
      setState(prev => {
        const newMessages = [...prev.messages]
        
        // Handle new structured event types from enhanced backend
        if (event.type === 'system_message') {
          // Skip system messages - these are internal setup messages
          console.log('Skipping system message:', event.content)
          return prev
          
        } else if (event.type === 'tool_message') {
          // Tool messages contain structured data (JSON) from workflow nodes
          // These could be displayed as structured analysis data if needed
          console.log('Received tool message:', event.content)
          return prev // For now, skip tool messages to keep UI clean
          
        } else if (event.type === 'ai_message') {
          // AI messages are the final human-like responses from Xiaomei
          if (event.content && event.metadata?.display !== false) {
            const content = event.content
            
            // Since backend sends complete messages, simulate streaming for better UX
            const existingIndex = newMessages.findIndex(msg => 
              msg.role === 'assistant' && msg.type === 'text'
            )
            
            if (existingIndex >= 0) {
              // Replace existing message with new complete content
              newMessages[existingIndex] = {
                ...newMessages[existingIndex],
                content: content // Replace with complete content
              }
            } else {
              // Create new Xiaomei message with complete content
              newMessages.push({
                id: event.message_id || 'xiaomei-ai',
                role: 'assistant',
                type: 'text',
                content: content,
                timestamp: new Date()
              })
            }
            
            return {
              ...prev,
              messages: newMessages,
              isStreaming: true, // Show as streaming for simulated effect
              error: null
            }
          }
          return prev
          
        } else if (event.type === 'text' && event.content) {
          // Legacy text events - process normally for backward compatibility
          const content = event.content.trim()
          
          const existingIndex = newMessages.findIndex(msg => 
            msg.role === 'assistant' && msg.type === 'text'
          )
          
          if (existingIndex >= 0) {
            // Update existing message (streaming)
            newMessages[existingIndex] = {
              ...newMessages[existingIndex],
              content: newMessages[existingIndex].content + content
            }
          } else {
            // Create new message
            newMessages.push({
              id: event.message_id || 'xiaomei-text',
              role: 'assistant',
              type: 'text',
              content: content,
              timestamp: new Date()
            })
          }
          
          return {
            ...prev,
            messages: newMessages,
            isStreaming: true,
            error: null
          }
          
        } else if (event.type === 'analysis' && event.result) {
          // Handle analysis results (fund analysis)
          const analysisContent = typeof event.result === 'string' ? 
            event.result : JSON.stringify(event.result, null, 2)
            
          newMessages.push({
            id: event.message_id || 'xiaomei-analysis',
            role: 'assistant',
            type: 'text',
            content: analysisContent,
            timestamp: new Date()
          })
          
          return {
            ...prev,
            messages: newMessages,
            isStreaming: false,
            error: null
          }
          
        } else if (event.type === 'image' && event.url) {
          // Handle image responses (if Xiaomei sends images)
          newMessages.push({
            id: event.message_id || 'xiaomei-image',
            role: 'assistant',
            type: 'image',
            content: event.url,
            timestamp: new Date()
          })
          
          return {
            ...prev,
            messages: newMessages,
            isStreaming: false,
            error: null
          }
          
        } else if (event.type === 'error') {
          // Handle errors
          console.error('Backend error:', event.message)
          return {
            ...prev,
            error: event.message || 'An error occurred',
            isStreaming: false
          }
        }
        
        return prev
      })
    } catch (error) {
      console.error('Event processing error:', error)
      setState(prev => ({
        ...prev,
        error: 'Error processing response',
        isStreaming: false
      }))
    }
  }, [])


  const handleFileUpload = useCallback(async (file: File) => {
    if (!state.session || !state.chatbot) {
      console.error('No active session or chatbot')
      setState(prev => ({
        ...prev,
        error: 'No active chat session. Please try refreshing the page.'
      }))
      return
    }

    // Validate file
    if (!file.type.startsWith('image/')) {
      setState(prev => ({
        ...prev,
        error: 'Please upload a valid image file (JPG, PNG, etc.)'
      }))
      return
    }

    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setState(prev => ({
        ...prev,
        error: 'Image file is too large. Please use an image smaller than 10MB.'
      }))
      return
    }

    try {
      const imageUrl = URL.createObjectURL(file)
      setState(prev => ({ 
        ...prev, 
        loading: true, 
        error: null,
        uploadedImage: imageUrl,
        messages: [], // Clear previous response - user wants fresh analysis
        isStreaming: true
      }))
      
      console.log('Sending image to chatbot:', {
        chatbotId: state.chatbot.id,
        sessionId: state.session.id,
        fileName: file.name,
        fileSize: file.size,
        fileType: file.type
      })
      
      // Send image to chatbot
      await api.sendImageMessage(
        state.chatbot.id,
        state.session.id,
        file,
        "请分析这个基金投资组合截图，提供详细的分析和建议。Please analyze this fund portfolio screenshot and provide detailed analysis and recommendations.",
        handleChatEvent
      )
      
    } catch (error) {
      console.error('Failed to send image:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to analyze image'
      setState(prev => ({
        ...prev,
        error: `Image upload failed: ${errorMessage}. Please check your connection and try again.`
      }))
    } finally {
      setState(prev => ({ 
        ...prev, 
        loading: false,
        isStreaming: false
      }))
    }
  }, [state.session, state.chatbot, handleChatEvent])


  const clearAnalysis = useCallback(() => {
    setState(prev => ({ 
      ...prev, 
      messages: [], 
      uploadedImage: null,
      isStreaming: false
    }))
  }, [])

  const handleStreamingComplete = useCallback(() => {
    setState(prev => ({ 
      ...prev, 
      isStreaming: false
    }))
  }, [])

  const clearImage = useCallback(() => {
    setState(prev => ({ 
      ...prev, 
      uploadedImage: null
    }))
  }, [])

  const retryInitialization = useCallback(() => {
    // Clear stored data and retry
    console.log('🔄 Retrying initialization...')
    localStorage.removeItem('auth_token')
    localStorage.removeItem('current_user')
    api.setToken('')
    setState(prev => ({
      ...prev,
      user: null,
      chatbot: null,
      session: null,
      error: null,
      initializing: true,
      messages: [],
      uploadedImage: null,
      isStreaming: false
    }))
    setTimeout(() => {
      initializeFundAnalysis()
    }, 100)
  }, [initializeFundAnalysis])


  if (state.initializing) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-white/80 backdrop-blur-sm rounded-3xl border border-slate-200/60 shadow-xl">
        <Loader2 className="w-12 h-12 animate-spin text-blue-500 mb-4" />
        <h3 className="text-xl font-semibold text-slate-900 mb-2">Initializing Fund Analysis</h3>
        <p className="text-slate-600 text-center max-w-md">
          Setting up your anonymous session and connecting to our AI-powered fund analysis system...
        </p>
      </div>
    )
  }

  if (state.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-3xl p-8 shadow-xl">
        <div className="flex items-center mb-4">
          <AlertCircle className="w-8 h-8 text-red-500 mr-3" />
          <h3 className="text-xl font-semibold text-red-800">Connection Error</h3>
        </div>
        <p className="text-red-700 mb-6">
          {state.error}
        </p>
        <div className="flex flex-col space-y-3">
          <p className="text-red-600 text-sm">
            ⚠️ Please ensure the WealthOS backend is running on http://localhost:8000
          </p>
          <button
            onClick={retryInitialization}
            className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-xl transition-colors font-medium"
          >
            Retry Connection
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Simple Header */}
      <div className="text-center py-6">
        <h2 className="text-2xl font-bold text-slate-900 mb-2">
          🤖 Xiaomei Fund Analyzer
        </h2>
        <p className="text-slate-600">
          Upload your portfolio screenshot for AI analysis
        </p>
        
        {state.chatbot && (
          <div className="mt-3 text-sm text-green-600">
            ✓ Connected to {state.chatbot.name}
          </div>
        )}
      </div>

      {/* Upload */}
      <ImageUpload
        onFileUpload={handleFileUpload}
        uploadedImage={state.uploadedImage}
        loading={state.loading}
        onClearImage={clearImage}
      />

      {/* Xiaomei's Analysis */}
      <AnalysisResult
        messages={state.messages}
        isStreaming={state.isStreaming}
        onClearAnalysis={clearAnalysis}
        onStreamingComplete={handleStreamingComplete}
      />
    </div>
  )
}

export default FundAnalysis 