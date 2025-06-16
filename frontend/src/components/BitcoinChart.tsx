import React, { useState, useEffect } from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface PriceData {
  timestamp: number
  price: number
}

interface BitcoinData {
  symbol: string
  current_price: number
  price_change_24h: number
  price_change_percent_24h: number
  high_24h: number
  low_24h: number
  historical_data: PriceData[]
}

const BitcoinChart: React.FC = () => {
  const [data, setData] = useState<BitcoinData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchBitcoinPrice = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/price/BTC/USD')
      if (!response.ok) throw new Error('Failed to fetch price')
      
      const priceData = await response.json()
      
      // Generate mock historical data for demo
      const mockHistoricalData: PriceData[] = []
      const currentPrice = parseFloat(priceData.price)
      const now = Date.now()
      
      for (let i = 23; i >= 0; i--) {
        const variation = (Math.random() - 0.5) * 0.05 // ±2.5% variation
        const price = currentPrice * (1 + variation * (Math.random() * 0.5))
        mockHistoricalData.push({
          timestamp: now - (i * 60 * 60 * 1000), // Every hour
          price: price
        })
      }
      
      const high24h = Math.max(...mockHistoricalData.map(d => d.price))
      const low24h = Math.min(...mockHistoricalData.map(d => d.price))
      const priceChange24h = currentPrice - mockHistoricalData[0].price
      const priceChangePercent24h = (priceChange24h / mockHistoricalData[0].price) * 100
      
      setData({
        symbol: priceData.symbol,
        current_price: currentPrice,
        price_change_24h: priceChange24h,
        price_change_percent_24h: priceChangePercent24h,
        high_24h: high24h,
        low_24h: low24h,
        historical_data: mockHistoricalData
      })
      setError(null)
    } catch (err) {
      setError('Failed to fetch Bitcoin price')
      console.error('Error fetching Bitcoin price:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchBitcoinPrice()
    const interval = setInterval(fetchBitcoinPrice, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price)
  }

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  }

  const CustomTooltip = ({ active, payload, label }: {
    active?: boolean;
    payload?: Array<{ value: number }>;
    label?: number;
  }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white/95 backdrop-blur-sm border border-gray-200 rounded-xl p-4 shadow-xl">
          <p className="text-gray-600 text-sm">{label ? formatTime(label) : ''}</p>
          <p className="text-lg font-bold text-gray-900">
            {formatPrice(payload[0].value)}
          </p>
        </div>
      )
    }
    return null
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading Bitcoin price...</span>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
        <div className="text-red-500 text-4xl mb-2">⚠️</div>
        <div className="text-red-700 font-medium mb-2">Failed to fetch Bitcoin price</div>
        <p className="text-red-600 text-sm mb-4">Make sure your WealthOS backend is running on http://localhost:8000</p>
        <button
          onClick={fetchBitcoinPrice}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          Retry
        </button>
      </div>
    )
  }

  const chartData = data.historical_data.map(item => ({
    ...item,
    time: formatTime(item.timestamp)
  }))

  const isPositive = data.price_change_percent_24h >= 0
  const chartColor = isPositive ? '#10B981' : '#EF4444'
  const gradientId = isPositive ? 'positiveGradient' : 'negativeGradient'

  return (
    <div className="space-y-8">
      {/* Price Header */}
      <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 shadow-lg border border-gray-100">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Bitcoin (BTC)</h2>
            <p className="text-gray-600">Real-time price tracking</p>
          </div>
          <p className="text-sm text-gray-500 bg-white px-3 py-1 rounded-full border">
            Powered by WealthOS Backend 🚀
          </p>
        </div>
        
        <div className="flex items-baseline space-x-4">
          <span className="text-5xl font-bold text-gray-900">
            {formatPrice(data.current_price)}
          </span>
          <div className={`flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium ${
            isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            <span>{isPositive ? '↗' : '↘'}</span>
            <span>{isPositive ? '+' : ''}{formatPrice(data.price_change_24h)}</span>
            <span>({isPositive ? '+' : ''}{data.price_change_percent_24h.toFixed(2)}%)</span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
        <div className="h-80">
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
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="price"
                stroke={chartColor}
                strokeWidth={3}
                fill={`url(#${gradientId})`}
                dot={false}
                activeDot={{ 
                  r: 6, 
                  fill: chartColor,
                  stroke: '#fff',
                  strokeWidth: 2,
                  filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.1))'
                }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-blue-700 font-medium">24h High</h3>
            <span className="text-blue-500 text-xl">📈</span>
          </div>
          <p className="text-2xl font-bold text-blue-900">{formatPrice(data.high_24h)}</p>
        </div>
        
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-purple-700 font-medium">24h Low</h3>
            <span className="text-purple-500 text-xl">📉</span>
          </div>
          <p className="text-2xl font-bold text-purple-900">{formatPrice(data.low_24h)}</p>
        </div>
        
        <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-6 border border-emerald-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-emerald-700 font-medium">Last Updated</h3>
            <span className="text-emerald-500 text-xl">🕐</span>
          </div>
          <p className="text-2xl font-bold text-emerald-900">
            {new Date().toLocaleTimeString('en-US', {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: true
            })}
          </p>
        </div>
      </div>
    </div>
  )
}

export default BitcoinChart 