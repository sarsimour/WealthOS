import React from 'react'
import { View, Text } from '@tarojs/components'
import './index.scss'

const Profile: React.FC = () => {
  return (
    <View className='profile-page'>
      <View className='header'>
        <Text className='title'>我的</Text>
      </View>
      
      <View className='content'>
        <View className='placeholder'>
          <Text className='placeholder-icon'>👤</Text>
          <Text className='placeholder-title'>个人中心</Text>
          <Text className='placeholder-desc'>这里将显示您的个人设置和账户信息</Text>
        </View>
      </View>
    </View>
  )
}

export default Profile 