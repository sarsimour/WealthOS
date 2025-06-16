import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

interface PriceData {
  timestamp: string
  price: number
  time: string
}

interface ApiResponse {
  symbol: string
  price: string
  timestamp: number
}

const fetchBitcoinPrice = async (): Promise<ApiResponse> => {
  // Connect to your WealthOS backend
  const response = await axios.get('http://localhost:8000/api/v1/price/BTC/USD')
  return response.data
}

const generateMockHistoricalData = (currentPrice: number): PriceData[] => {
  const data: PriceData[] = []
  const now = new Date()
  
  for (let i = 23; i >= 0; i--) {
    const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000)
    const variation = (Math.random() - 0.5) * 0.1 // ±5% variation
    const price = currentPrice * (1 + variation * (i / 24))
    
    data.push({
      timestamp: timestamp.toISOString(),
      price: Math.round(price * 100) / 100,
      time: timestamp.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    })
  }
  
  return data
}

export default function BitcoinChart() {
  const [historicalData, setHistoricalData] = useState<PriceData[]>([])

  const { data: currentPrice, isLoading, error, refetch } = useQuery({
    queryKey: ['bitcoin-price'],
    queryFn: fetchBitcoinPrice,
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: 3,
  })

  useEffect(() => {
    if (currentPrice) {
      const mockData = generateMockHistoricalData(parseFloat(currentPrice.price))
      setHistoricalData(mockData)
    }
  }, [currentPrice])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        <span className="ml-2">Loading Bitcoin price...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4">
        <div className="text-destructive">
          ⚠️ Failed to fetch Bitcoin price
        </div>
        <p className="text-sm text-muted-foreground">
          Make sure your WealthOS backend is running on http://localhost:8000
        </p>
        <button 
          onClick={() => refetch()}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
        >
          Retry
        </button>
      </div>
    )
  }

  const currentPriceValue = currentPrice ? parseFloat(currentPrice.price) : 0
  const priceChange = historicalData.length > 1 
    ? currentPriceValue - historicalData[0].price 
    : 0
  const priceChangePercent = historicalData.length > 1 
    ? (priceChange / historicalData[0].price) * 100 
    : 0

  return (
    <div className="space-y-6">
      {/* Price Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Bitcoin (BTC)</h2>
          <p className="text-muted-foreground">Real-time price tracking</p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold">
            ${currentPriceValue.toLocaleString()}
          </div>
          <div className={`flex items-center ${priceChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            <span>{priceChange >= 0 ? '↗' : '↘'}</span>
            <span className="ml-1">
              {priceChange >= 0 ? '+' : ''}${priceChange.toFixed(2)} 
              ({priceChangePercent >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%)
            </span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-96 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={historicalData}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis 
              dataKey="time" 
              tick={{ fontSize: 12 }}
              tickLine={false}
            />
            <YAxis 
              domain={['dataMin - 1000', 'dataMax + 1000']}
              tick={{ fontSize: 12 }}
              tickLine={false}
              tickFormatter={(value) => `$${value.toLocaleString()}`}
            />
            <Tooltip 
              formatter={(value: number) => [`$${value.toLocaleString()}`, 'Price']}
              labelFormatter={(label) => `Time: ${label}`}
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '6px',
              }}
            />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke="hsl(var(--primary))" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: 'hsl(var(--primary))' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-card p-4 rounded-lg border">
          <div className="text-sm text-muted-foreground">24h High</div>
          <div className="text-lg font-semibold">
            ${Math.max(...historicalData.map(d => d.price)).toLocaleString()}
          </div>
        </div>
        <div className="bg-card p-4 rounded-lg border">
          <div className="text-sm text-muted-foreground">24h Low</div>
          <div className="text-lg font-semibold">
            ${Math.min(...historicalData.map(d => d.price)).toLocaleString()}
          </div>
        </div>
        <div className="bg-card p-4 rounded-lg border">
          <div className="text-sm text-muted-foreground">Last Updated</div>
          <div className="text-lg font-semibold">
            {currentPrice ? new Date(currentPrice.timestamp * 1000).toLocaleTimeString() : 'N/A'}
          </div>
        </div>
      </div>
    </div>
  )
} 