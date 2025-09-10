import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
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
 * Now supports Markdown rendering.
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
      <div className="prose prose-slate max-w-none">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight]}
          components={{
            // Custom components for better styling
            h1: ({ children }) => <h1 className="text-2xl font-bold text-slate-900 mb-4">{children}</h1>,
            h2: ({ children }) => <h2 className="text-xl font-semibold text-slate-800 mb-3">{children}</h2>,
            h3: ({ children }) => <h3 className="text-lg font-medium text-slate-800 mb-2">{children}</h3>,
            h4: ({ children }) => <h4 className="text-base font-medium text-slate-700 mb-2">{children}</h4>,
            p: ({ children }) => <p className="text-slate-700 mb-3 leading-relaxed">{children}</p>,
            ul: ({ children }) => <ul className="list-disc list-inside mb-3 text-slate-700 space-y-1">{children}</ul>,
            ol: ({ children }) => <ol className="list-decimal list-inside mb-3 text-slate-700 space-y-1">{children}</ol>,
            li: ({ children }) => <li className="text-slate-700">{children}</li>,
            strong: ({ children }) => <strong className="font-semibold text-slate-900">{children}</strong>,
            em: ({ children }) => <em className="italic text-slate-800">{children}</em>,
            code: ({ children, className }) => {
              const isInline = !className
              if (isInline) {
                return <code className="bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded text-sm font-mono">{children}</code>
              }
              return <code className={className}>{children}</code>
            },
            pre: ({ children }) => (
              <pre className="bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto mb-4">
                {children}
              </pre>
            ),
            blockquote: ({ children }) => (
              <blockquote className="border-l-4 border-blue-500 pl-4 py-2 mb-4 bg-blue-50 text-slate-700 italic">
                {children}
              </blockquote>
            ),
            table: ({ children }) => (
              <table className="w-full border-collapse border border-slate-300 mb-4">
                {children}
              </table>
            ),
            th: ({ children }) => (
              <th className="border border-slate-300 bg-slate-100 px-3 py-2 text-left font-semibold text-slate-900">
                {children}
              </th>
            ),
            td: ({ children }) => (
              <td className="border border-slate-300 px-3 py-2 text-slate-700">
                {children}
              </td>
            ),
            a: ({ children, href }) => (
              <a href={href} className="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener noreferrer">
                {children}
              </a>
            ),
          }}
        >
          {displayedText}
        </ReactMarkdown>
      </div>
      {isStreaming && (
        <span className="inline-block w-0.5 h-5 bg-blue-500 ml-1 animate-pulse" />
      )}
    </div>
  )
}

export default StreamingText