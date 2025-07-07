import React, { useState, useEffect } from 'react'
import { View, Text, Canvas } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { api, formatPrice, formatPercentage, HistoryDataPoint, BitcoinPrice } from '../../utils/api'
import './index.scss'

interface MarketState {
  currentPrice: BitcoinPrice | null
  historyData: HistoryDataPoint[]
  loading: boolean
  selectedTimeframe: string
  changePercent: number
}

const Market: React.FC = () => {
  const [state, setState] = useState<MarketState>({
    currentPrice: null,
    historyData: [],
    loading: true,
    selectedTimeframe: '7d',
    changePercent: 0
  })

  const timeframes = [
    { label: '1天', value: '1d' },
    { label: '7天', value: '7d' },
    { label: '30天', value: '30d' },
    { label: '90天', value: '90d' }
  ]

  // 获取比特币价格数据
  const fetchBitcoinData = async (period: string = '7d') => {
    try {
      setState(prev => ({ ...prev, loading: true }))
      
      // 并行获取当前价格和历史数据
      const [priceResult, historyResult] = await Promise.all([
        api.getBitcoinPrice(),
        api.getBitcoinHistory(period)
      ])

      // 计算价格变化百分比
      const historyData = historyResult.data || []
      const changePercent = historyData.length > 1 
        ? ((priceResult.price - historyData[0].price) / historyData[0].price) * 100
        : 0

      setState(prev => ({
        ...prev,
        currentPrice: priceResult,
        historyData,
        changePercent,
        loading: false
      }))

      // 绘制图表
      if (historyData.length > 0) {
        drawChart(historyData)
      }
    } catch (error) {
      console.error('获取比特币数据失败:', error)
      Taro.showToast({
        title: '数据获取失败',
        icon: 'error'
      })
      setState(prev => ({ ...prev, loading: false }))
    }
  }

  // 绘制价格图表
  const drawChart = (data: HistoryDataPoint[]) => {
    const query = Taro.createSelectorQuery()
    query.select('#bitcoin-chart')
      .fields({ node: true, size: true })
      .exec((res) => {
        if (res[0]) {
          const canvas = res[0].node
          const ctx = canvas.getContext('2d')
          const { width, height } = res[0]
          
          // 设置画布尺寸
          canvas.width = width * 2 // 高分辨率
          canvas.height = height * 2
          ctx.scale(2, 2)

          // 清空画布
          ctx.clearRect(0, 0, width, height)

          if (data.length < 2) return

          // 计算坐标
          const padding = 20
          const chartWidth = width - padding * 2
          const chartHeight = height - padding * 2

          const prices = data.map(d => d.price)
          const minPrice = Math.min(...prices)
          const maxPrice = Math.max(...prices)
          const priceRange = maxPrice - minPrice

          // 绘制网格线
          ctx.strokeStyle = '#f0f0f0'
          ctx.lineWidth = 1
          for (let i = 0; i <= 4; i++) {
            const y = padding + (chartHeight / 4) * i
            ctx.beginPath()
            ctx.moveTo(padding, y)
            ctx.lineTo(width - padding, y)
            ctx.stroke()
          }

          // 绘制价格线
          ctx.strokeStyle = state.changePercent >= 0 ? '#4CAF50' : '#f44336'
          ctx.lineWidth = 2
          ctx.beginPath()

          data.forEach((point, index) => {
            const x = padding + (chartWidth / (data.length - 1)) * index
            const y = padding + chartHeight - ((point.price - minPrice) / priceRange) * chartHeight

            if (index === 0) {
              ctx.moveTo(x, y)
            } else {
              ctx.lineTo(x, y)
            }
          })

          ctx.stroke()

          // 绘制填充区域
          ctx.globalAlpha = 0.1
          ctx.fillStyle = state.changePercent >= 0 ? '#4CAF50' : '#f44336'
          ctx.lineTo(width - padding, padding + chartHeight)
          ctx.lineTo(padding, padding + chartHeight)
          ctx.fill()
        }
      })
  }

  // 切换时间周期
  const handleTimeframeChange = (period: string) => {
    setState(prev => ({ ...prev, selectedTimeframe: period }))
    fetchBitcoinData(period)
  }

  // 下拉刷新
  const onPullDownRefresh = () => {
    fetchBitcoinData(state.selectedTimeframe)
    setTimeout(() => {
      Taro.stopPullDownRefresh()
    }, 1000)
  }

  useEffect(() => {
    fetchBitcoinData()
  }, [])

  // 注册下拉刷新事件
  Taro.usePullDownRefresh(onPullDownRefresh)

  return (
    <View className='market-page'>
      {/* 价格头部 */}
      <View className='price-header'>
        <View className='coin-info'>
          <Text className='coin-name'>比特币 (BTC)</Text>
          <Text className='current-price'>
            {state.currentPrice ? formatPrice(state.currentPrice.price) : '加载中...'}
          </Text>
          <View className={`price-change ${state.changePercent >= 0 ? 'positive' : 'negative'}`}>
            <Text className='change-icon'>{state.changePercent >= 0 ? '↗' : '↘'}</Text>
            <Text className='change-text'>{formatPercentage(state.changePercent)}</Text>
          </View>
        </View>
        <View className='refresh-btn' onClick={() => fetchBitcoinData(state.selectedTimeframe)}>
          <Text className='refresh-icon'>🔄</Text>
        </View>
      </View>

      {/* 时间周期选择器 */}
      <View className='timeframe-selector'>
        {timeframes.map((item) => (
          <View
            key={item.value}
            className={`timeframe-item ${state.selectedTimeframe === item.value ? 'active' : ''}`}
            onClick={() => handleTimeframeChange(item.value)}
          >
            <Text>{item.label}</Text>
          </View>
        ))}
      </View>

      {/* 图表区域 */}
      <View className='chart-container'>
        {state.loading ? (
          <View className='loading'>
            <Text>加载中...</Text>
          </View>
        ) : (
          <Canvas 
            id='bitcoin-chart'
            type='2d'
            className='chart-canvas'
          />
        )}
      </View>

      {/* 市场数据 */}
      <View className='market-stats'>
        <View className='stat-item'>
          <Text className='stat-label'>24h 最高</Text>
          <Text className='stat-value'>
            {state.currentPrice ? formatPrice(state.currentPrice.price * 1.02) : '--'}
          </Text>
        </View>
        <View className='stat-item'>
          <Text className='stat-label'>24h 最低</Text>
          <Text className='stat-value'>
            {state.currentPrice ? formatPrice(state.currentPrice.price * 0.98) : '--'}
          </Text>
        </View>
        <View className='stat-item'>
          <Text className='stat-label'>市值</Text>
          <Text className='stat-value'>5.58万亿</Text>
        </View>
        <View className='stat-item'>
          <Text className='stat-label'>24h 成交量</Text>
          <Text className='stat-value'>235.6亿</Text>
        </View>
      </View>
    </View>
  )
}

export default Market 