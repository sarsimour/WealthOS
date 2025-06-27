import React, { useState, useEffect } from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Tabs, TabsList, TabsTrigger } from './ui/tabs'
import { API_BASE_URL, getCurrentApiInfo, isMockMode } from '../config/api'

interface HistoricalPricePoint {
  timestamp: number
  price: number
  volume?: number
}

interface HistoricalData {
  symbol: string
  currency: string
  period: string
  interval: string
  data: HistoricalPricePoint[]
  metadata: {
    total_points: number
    start_time: string
    end_time: string
    interval: string
  }
}

interface FullBitcoinData {
  symbol: string
  current_price: number
  price_change_24h: number
  price_change_percent_24h: number
  high_24h: number
  low_24h: number
  historical_data: HistoricalPricePoint[]
  currency: string
  last_updated: string
}

type TimeFrame = '1d' | '7d' | '30d' | '90d' | '1y'

const BitcoinChart: React.FC = () => {
  const [currentData, setCurrentData] = useState<FullBitcoinData | null>(null)
  const [historicalData, setHistoricalData] = useState<HistoricalData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTimeframe, setSelectedTimeframe] = useState<TimeFrame>('7d')
  
  const apiInfo = getCurrentApiInfo()

  const timeframes: { value: TimeFrame; label: string }[] = [
    { value: '1d', label: '1D' },
    { value: '7d', label: '7D' },
    { value: '30d', label: '30D' },
    { value: '90d', label: '90D' },
    { value: '1y', label: '1Y' },
  ]

  const fetchCurrentData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/prices/bitcoin/full?days=1`)
      if (!response.ok) throw new Error('Failed to fetch current Bitcoin data')
      const data = await response.json()
      setCurrentData(data)
    } catch (err) {
      console.error('Error fetching current Bitcoin data:', err)
      setError('Failed to fetch current Bitcoin data')
    }
  }

  const fetchHistoricalData = async (timeframe: TimeFrame) => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/prices/bitcoin/history?period=${timeframe}`)
      if (!response.ok) throw new Error('Failed to fetch historical Bitcoin data')
      const data = await response.json()
      setHistoricalData(data)
      setError(null)
    } catch (err) {
      console.error('Error fetching historical Bitcoin data:', err)
      setError('Failed to fetch historical Bitcoin data')
    } finally {
      setLoading(false)
    }
  }

  // Fetch current data on mount and set up interval
  useEffect(() => {
    fetchCurrentData()
    const interval = setInterval(fetchCurrentData, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])

  // Fetch historical data when timeframe changes
  useEffect(() => {
    fetchHistoricalData(selectedTimeframe)
  }, [selectedTimeframe])

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price)
  }

  const formatDetailedPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price)
  }

  const formatTime = (timestamp: number, timeframe: TimeFrame) => {
    const date = new Date(timestamp)
    
    switch (timeframe) {
      case '1d':
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      case '7d':
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      case '30d':
      case '90d':
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      case '1y':
        return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })
      default:
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }
  }

  const CustomTooltip = ({ active, payload, label }: {
    active?: boolean;
    payload?: Array<{ value: number }>;
    label?: number;
  }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white/95 backdrop-blur-sm border border-gray-200 rounded-xl p-4 shadow-xl">
          <p className="text-gray-600 text-sm">
            {label ? new Date(label).toLocaleString('en-US', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            }) : ''}
          </p>
          <p className="text-lg font-bold text-gray-900">
            {formatDetailedPrice(payload[0].value)}
          </p>
        </div>
      )
    }
    return null
  }

  if (loading && !historicalData) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading Bitcoin data...</span>
      </div>
    )
  }

  if (error && !historicalData) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
        <div className="text-red-500 text-4xl mb-2">⚠️</div>
        <div className="text-red-700 font-medium mb-2">Failed to fetch Bitcoin data</div>
        <p className="text-red-600 text-sm mb-4">
          Make sure your WealthOS backend is running on http://localhost:8001
        </p>
        <button
          onClick={() => fetchHistoricalData(selectedTimeframe)}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          Retry
        </button>
      </div>
    )
  }

  const chartData = historicalData?.data.map(item => ({
    ...item,
    time: formatTime(item.timestamp, selectedTimeframe)
  })) || []

  const isPositive = currentData ? currentData.price_change_percent_24h >= 0 : true
  const chartColor = isPositive ? '#10B981' : '#EF4444'
  const gradientId = isPositive ? 'positiveGradient' : 'negativeGradient'

  return (
    <div className="space-y-8">
      {/* Price Header */}
      {currentData && (
        <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Bitcoin (BTC)</h2>
              <p className="text-gray-600">Real-time price tracking powered by Binance</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500 bg-white px-3 py-1 rounded-full border">
                Live via Binance 🚀
              </p>
              <p className="text-xs text-gray-400 mt-1">Updated every 30s</p>
            </div>
          </div>
          
          <div className="flex items-baseline space-x-4">
            <span className="text-5xl font-bold text-gray-900">
              {formatPrice(currentData.current_price || 0)}
            </span>
            <div className={`flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium ${
              isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>
              <span>{isPositive ? '↗' : '↘'}</span>
              <span>{isPositive ? '+' : ''}{formatDetailedPrice(currentData.price_change_24h || 0)}</span>
              <span>({isPositive ? '+' : ''}{(currentData.price_change_percent_24h || 0).toFixed(2)}%)</span>
            </div>
          </div>

          {/* 24h Stats */}
          <div className="grid grid-cols-2 gap-4 mt-6">
            <div className="bg-white rounded-lg p-4 border border-gray-100">
              <p className="text-sm text-gray-600">24h High</p>
              <p className="text-lg font-semibold text-gray-900">{formatPrice(currentData.high_24h || 0)}</p>
            </div>
            <div className="bg-white rounded-lg p-4 border border-gray-100">
              <p className="text-sm text-gray-600">24h Low</p>
              <p className="text-lg font-semibold text-gray-900">{formatPrice(currentData.low_24h || 0)}</p>
            </div>
          </div>
        </div>
      )}

      {/* Chart Section */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-semibold text-gray-900">Bitcoin Price History</h3>
            <p className="text-sm text-gray-500">Historical price movements across different timeframes</p>
          </div>
          
          <div className="flex items-center gap-4">
            {/* API Source Display */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Data:</span>
              <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                isMockMode() 
                  ? 'bg-blue-100 text-blue-800 border border-blue-200' 
                  : 'bg-green-100 text-green-800 border border-green-200'
              }`}>
                {isMockMode() ? '🎭 Mock' : '🔗 Real'}
              </div>
              <span className="text-xs text-gray-500">
                ({apiInfo.description})
              </span>
            </div>

            {/* Timeframe Selector */}
            <Tabs value={selectedTimeframe} onValueChange={(value) => setSelectedTimeframe(value as TimeFrame)}>
              <TabsList className="grid w-full grid-cols-5">
                {timeframes.map((tf) => (
                  <TabsTrigger key={tf.value} value={tf.value} className="px-4 py-2">
                    {tf.label}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          </div>
        </div>

        {/* Chart */}
        <div className="h-96">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Loading {selectedTimeframe} data...</span>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="positiveGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.05}/>
                  </linearGradient>
                  <linearGradient id="negativeGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0.05}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" opacity={0.5} />
                <XAxis 
                  dataKey="time" 
                  stroke="#6B7280"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis 
                  stroke="#6B7280"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => formatPrice(value)}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke={chartColor}
                  strokeWidth={2}
                  fill={`url(#${gradientId})`}
                  fillOpacity={1}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Chart Info */}
        {historicalData && historicalData.metadata && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Data Points:</span>
                <span className="ml-2 font-medium">{historicalData.metadata?.total_points || 0}</span>
              </div>
              <div>
                <span className="text-gray-600">Interval:</span>
                <span className="ml-2 font-medium">{historicalData.metadata?.interval || 'N/A'}</span>
              </div>
              <div>
                <span className="text-gray-600">Period:</span>
                <span className="ml-2 font-medium">{historicalData.period || 'N/A'}</span>
              </div>
              <div>
                <span className="text-gray-600">Currency:</span>
                <span className="ml-2 font-medium">{historicalData.currency?.toUpperCase() || 'USD'}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default BitcoinChart 