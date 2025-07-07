import React, { useState, useEffect } from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { api, formatPrice, formatPercentage, BitcoinPrice } from '../../utils/api'
import './index.scss'

interface PortfolioState {
  bitcoinPrice: BitcoinPrice | null
  totalAssets: number
  todayProfit: number
  totalReturn: number
  holdings: Array<{
    name: string
    symbol: string
    amount: number
    value: number
    changePercent: number
  }>
  loading: boolean
}

const Index: React.FC = () => {
  const [state, setState] = useState<PortfolioState>({
    bitcoinPrice: null,
    totalAssets: 125430.50,
    todayProfit: 3010.33,
    totalReturn: 25.8,
    holdings: [
      { name: '比特币', symbol: 'BTC', amount: 0.5, value: 95000, changePercent: 2.4 },
      { name: '以太坊', symbol: 'ETH', amount: 2.5, value: 18000, changePercent: -0.8 },
      { name: '币安币', symbol: 'BNB', amount: 5, value: 12430, changePercent: 1.2 }
    ],
    loading: true
  })

  const fetchData = async () => {
    try {
      setState(prev => ({ ...prev, loading: true }))
      
      // 获取比特币价格用于投资组合计算
      const bitcoinPrice = await api.getBitcoinPrice()
      
      // 更新投资组合数据（在真实应用中，这里应该调用用户投资组合API）
      const updatedHoldings = state.holdings.map(holding => {
        if (holding.symbol === 'BTC') {
          return {
            ...holding,
            value: holding.amount * bitcoinPrice.price * 7.2 // 转换为人民币
          }
        }
        return holding
      })

      const totalAssets = updatedHoldings.reduce((sum, h) => sum + h.value, 0)

      setState(prev => ({
        ...prev,
        bitcoinPrice,
        holdings: updatedHoldings,
        totalAssets,
        loading: false
      }))
    } catch (error) {
      console.error('获取数据失败:', error)
      setState(prev => ({ ...prev, loading: false }))
    }
  }

  const navigateToMarket = () => {
    Taro.switchTab({
      url: '/pages/market/index'
    })
  }

  const navigateToPortfolio = () => {
    Taro.switchTab({
      url: '/pages/portfolio/index'
    })
  }

  // 下拉刷新
  const onPullDownRefresh = () => {
    fetchData()
    setTimeout(() => {
      Taro.stopPullDownRefresh()
    }, 1000)
  }

  useEffect(() => {
    fetchData()
  }, [])

  // 注册下拉刷新事件
  Taro.usePullDownRefresh(onPullDownRefresh)

  return (
    <View className='index-page'>
      {/* 用户欢迎区域 */}
      <View className='header'>
        <View className='user-greeting'>
          <Text className='greeting-text'>你好，投资者</Text>
          <Text className='subtitle'>欢迎使用 WealthOS</Text>
        </View>
        <View className='settings-btn'>
          <Text className='icon'>⚙️</Text>
        </View>
      </View>

      {/* 投资组合概览 */}
      <View className='portfolio-summary'>
        <View className='summary-card'>
          <Text className='label'>总资产</Text>
          <Text className='amount'>{formatPrice(state.totalAssets / 7.2)}</Text>
          <View className='change positive'>
            <Text className='change-icon'>↗</Text>
            <Text className='change-text'>{formatPercentage(state.totalReturn)}</Text>
            <Text className='change-amount'>({formatPrice(state.todayProfit / 7.2)})</Text>
          </View>
        </View>

        <View className='stats-grid'>
          <View className='stat-item'>
            <Text className='stat-label'>今日收益</Text>
            <Text className='stat-value positive'>{formatPrice(state.todayProfit / 7.2)}</Text>
          </View>
          <View className='stat-item'>
            <Text className='stat-label'>总收益率</Text>
            <Text className='stat-value positive'>{formatPercentage(state.totalReturn)}</Text>
          </View>
          <View className='stat-item'>
            <Text className='stat-label'>持仓数量</Text>
            <Text className='stat-value'>{state.holdings.length}</Text>
          </View>
          <View className='stat-item'>
            <Text className='stat-label'>当前价格</Text>
            <Text className='stat-value'>
              {state.bitcoinPrice ? formatPrice(state.bitcoinPrice.price) : '加载中...'}
            </Text>
          </View>
        </View>
      </View>

      {/* 快速操作 */}
      <View className='quick-actions'>
        <View className='action-item' onClick={navigateToMarket}>
          <View className='action-icon'>📊</View>
          <Text className='action-label'>查看行情</Text>
        </View>
        <View className='action-item' onClick={navigateToPortfolio}>
          <View className='action-icon'>💰</View>
          <Text className='action-label'>投资组合</Text>
        </View>
        <View className='action-item'>
          <View className='action-icon'>📈</View>
          <Text className='action-label'>添加投资</Text>
        </View>
        <View className='action-item'>
          <View className='action-icon'>📋</View>
          <Text className='action-label'>交易记录</Text>
        </View>
      </View>

      {/* 持仓列表 */}
      <View className='holdings-list'>
        <View className='section-header'>
          <Text className='section-title'>我的持仓</Text>
          <Text className='see-all' onClick={navigateToPortfolio}>查看全部</Text>
        </View>
        
        {state.holdings.map((holding, index) => (
          <View key={index} className='holding-item'>
            <View className='holding-info'>
              <Text className='holding-name'>{holding.name}</Text>
              <Text className='holding-symbol'>{holding.symbol}</Text>
            </View>
            <View className='holding-amount'>
              <Text className='amount-text'>{holding.amount}</Text>
            </View>
            <View className='holding-value'>
              <Text className='value-text'>{formatPrice(holding.value / 7.2)}</Text>
              <Text className={`change-text ${holding.changePercent >= 0 ? 'positive' : 'negative'}`}>
                {formatPercentage(holding.changePercent)}
              </Text>
            </View>
          </View>
        ))}
      </View>

      {/* 市场快讯 */}
      <View className='market-news'>
        <View className='section-header'>
          <Text className='section-title'>市场快讯</Text>
        </View>
        <View className='news-item'>
          <Text className='news-title'>比特币突破新高，投资者情绪高涨</Text>
          <Text className='news-time'>2小时前</Text>
        </View>
        <View className='news-item'>
          <Text className='news-title'>以太坊2.0升级进展顺利</Text>
          <Text className='news-time'>4小时前</Text>
        </View>
      </View>
    </View>
  )
}

export default Index
