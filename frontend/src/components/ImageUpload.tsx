import React, { useCallback, useState } from 'react'

interface ImageUploadProps {
  onFileUpload: (file: File) => void
  uploadedImage: string | null
  loading: boolean
  onClearImage: () => void
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  onFileUpload,
  uploadedImage,
  loading,
  onClearImage
}) => {
  const [dragOver, setDragOver] = useState(false)

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    
    const files = Array.from(e.dataTransfer.files)
    const imageFile = files.find(file => file.type.startsWith('image/'))
    
    if (imageFile) {
      onFileUpload(imageFile)
    }
  }, [onFileUpload])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }, [])

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type.startsWith('image/')) {
      onFileUpload(file)
    }
  }, [onFileUpload])

  // If image is uploaded, show simple preview
  if (uploadedImage) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-4">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-slate-700">📊 Portfolio Image</span>
          <button
            onClick={onClearImage}
            disabled={loading}
            className="text-slate-400 hover:text-slate-600 text-sm"
          >
            ✕
          </button>
        </div>
        <img
          src={uploadedImage}
          alt="Portfolio"
          className="w-full h-auto rounded max-h-48 object-contain"
        />
        {loading && (
          <div className="mt-2 text-center text-sm text-slate-500">
            📈 Analyzing...
          </div>
        )}
      </div>
    )
  }

  // Upload area
  return (
    <div
      className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all ${
        dragOver ? 'border-blue-400 bg-blue-50' : 'border-slate-300 bg-white'
      }`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <input
        type="file"
        accept="image/*"
        onChange={handleFileInputChange}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        disabled={loading}
      />
      
      <div className="space-y-4">
        <div className="text-4xl">📤</div>
        <div>
          <h3 className="text-lg font-semibold text-slate-900 mb-2">
            Upload Portfolio Screenshot
          </h3>
          <p className="text-slate-600 text-sm">
            Drop your fund portfolio image here or click to browse
          </p>
        </div>
      </div>
    </div>
  )
}

export default ImageUpload