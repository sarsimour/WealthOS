import React from 'react'
import { Loader2 } from 'lucide-react'
import type { FrontendMessage } from '../lib/api'
import StreamingText from './StreamingText'

interface AnalysisResultProps {
  messages: FrontendMessage[]
  isStreaming: boolean
  onClearAnalysis: () => void
  onStreamingComplete?: () => void
}

const AnalysisResult: React.FC<AnalysisResultProps> = ({
  messages,
  isStreaming,
  onClearAnalysis,
  onStreamingComplete
}) => {
  // Only show assistant messages (Xiaomei's responses)
  const xiaomeiMessages = messages.filter(msg => msg.role === 'assistant')

  // Don't show anything if no responses and not streaming
  if (xiaomeiMessages.length === 0 && !isStreaming) {
    return null
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-900">💡 Xiaomei's Analysis</h3>
        <button
          onClick={onClearAnalysis}
          className="text-slate-500 hover:text-slate-700 px-3 py-1 rounded text-sm"
        >
          Clear
        </button>
      </div>

      {/* Show all Xiaomei responses */}
      <div className="space-y-4">
        {xiaomeiMessages.map((message, index) => (
          <div key={message.id || index}>
            {message.type === 'text' && (
              <StreamingText
                text={message.content}
                speed={35} // Slightly faster for better UX
                enabled={true}
                className="text-slate-800 leading-relaxed"
                onComplete={() => {
                  // Call parent callback when text streaming completes
                  onStreamingComplete?.()
                }}
              />
            )}
            {message.type === 'image' && (
              <img
                src={message.content}
                alt="Xiaomei's response"
                className="max-w-full h-auto rounded-lg"
              />
            )}
          </div>
        ))}
        
        {/* Streaming indicator */}
        {isStreaming && (
          <div className="flex items-center space-x-2 text-slate-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Xiaomei is analyzing...</span>
            <span className="inline-block w-0.5 h-5 bg-blue-500 ml-1 animate-pulse" />
          </div>
        )}
      </div>

      {/* Show loading state when no messages yet but streaming */}
      {xiaomeiMessages.length === 0 && isStreaming && (
        <div className="flex items-center space-x-2 text-slate-500 py-8 justify-center">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Xiaomei is thinking...</span>
        </div>
      )}
    </div>
  )
}

export default AnalysisResult