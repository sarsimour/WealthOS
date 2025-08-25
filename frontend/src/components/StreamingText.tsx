import React from 'react'
import { useStreamingText } from '../hooks/useStreamingText'

interface StreamingTextProps {
  text: string
  speed?: number
  enabled?: boolean
  className?: string
  onComplete?: () => void
}

/**
 * StreamingText component that displays text character-by-character
 * with a blinking cursor during streaming animation.
 */
const StreamingText: React.FC<StreamingTextProps> = ({
  text,
  speed = 40,
  enabled = true,
  className = '',
  onComplete
}) => {
  const { displayedText, isStreaming, skip } = useStreamingText(text, {
    speed,
    enabled,
    onComplete
  })

  return (
    <div 
      className={`${className} ${isStreaming ? 'cursor-pointer' : ''}`}
      onClick={isStreaming ? skip : undefined}
      title={isStreaming ? 'Click to skip animation' : ''}
    >
      <span className="whitespace-pre-wrap">{displayedText}</span>
      {isStreaming && (
        <span className="inline-block w-0.5 h-5 bg-blue-500 ml-1 animate-pulse" />
      )}
    </div>
  )
}

export default StreamingText