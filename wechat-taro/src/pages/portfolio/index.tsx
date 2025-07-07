import React from 'react'
import { View, Text } from '@tarojs/components'
import './index.scss'

const Portfolio: React.FC = () => {
  return (
    <View className='portfolio-page'>
      <View className='header'>
        <Text className='title'>投资组合</Text>
      </View>
      
      <View className='content'>
        <View className='placeholder'>
          <Text className='placeholder-icon'>📊</Text>
          <Text className='placeholder-title'>投资组合详情</Text>
          <Text className='placeholder-desc'>这里将显示您的详细投资组合信息</Text>
        </View>
      </View>
    </View>
  )
}

export default Portfolio 