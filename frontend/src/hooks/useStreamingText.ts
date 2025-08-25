import { useState, useEffect, useCallback } from 'react'

interface StreamingOptions {
  speed?: number // milliseconds per character
  enabled?: boolean // can disable streaming
  onComplete?: () => void // callback when streaming finishes
}

interface StreamingState {
  displayedText: string
  isStreaming: boolean
  progress: number // 0-1
  skip: () => void // function to skip to end
}

/**
 * Custom hook for simulating character-by-character text streaming.
 * Provides smooth UX while backend sends complete messages.
 */
export const useStreamingText = (
  fullText: string,
  options: StreamingOptions = {}
): StreamingState => {
  const {
    speed = 40, // 40ms per character = ~25 chars/second (readable speed)
    enabled = true,
    onComplete
  } = options

  const [displayedText, setDisplayedText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isStreaming, setIsStreaming] = useState(false)
  const [shouldSkip, setShouldSkip] = useState(false)

  // Reset when fullText changes
  useEffect(() => {
    if (!fullText) {
      setDisplayedText('')
      setCurrentIndex(0)
      setIsStreaming(false)
      setShouldSkip(false)
      return
    }

    // If streaming is disabled, show full text immediately
    if (!enabled) {
      setDisplayedText(fullText)
      setCurrentIndex(fullText.length)
      setIsStreaming(false)
      setShouldSkip(false)
      return
    }

    // Start streaming from beginning
    setDisplayedText('')
    setCurrentIndex(0)
    setIsStreaming(true)
    setShouldSkip(false)
  }, [fullText, enabled])

  // Streaming animation effect
  useEffect(() => {
    if (!isStreaming || !fullText || currentIndex >= fullText.length) {
      if (isStreaming) {
        setIsStreaming(false)
        onComplete?.()
      }
      return
    }

    // Skip to end if requested
    if (shouldSkip) {
      setDisplayedText(fullText)
      setCurrentIndex(fullText.length)
      setIsStreaming(false)
      onComplete?.()
      return
    }

    const timer = setTimeout(() => {
      const nextIndex = currentIndex + 1
      setDisplayedText(fullText.substring(0, nextIndex))
      setCurrentIndex(nextIndex)
    }, speed)

    return () => clearTimeout(timer)
  }, [currentIndex, isStreaming, fullText, speed, shouldSkip, onComplete])

  // Skip function to jump to end
  const skip = useCallback(() => {
    setShouldSkip(true)
  }, [])

  const progress = fullText ? currentIndex / fullText.length : 0

  return {
    displayedText: displayedText || fullText,
    isStreaming,
    progress,
    skip
  }
}