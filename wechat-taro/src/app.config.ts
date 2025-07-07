export default defineAppConfig({
  pages: [
    'pages/index/index',
    'pages/market/index',
    'pages/portfolio/index',
    'pages/profile/index'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#2196F3',
    navigationBarTitleText: 'WealthOS',
    navigationBarTextStyle: 'white',
    backgroundColor: '#f5f5f5'
  },
  tabBar: {
    color: '#999999',
    selectedColor: '#2196F3',
    backgroundColor: '#ffffff',
    borderStyle: 'black',
    list: [
      {
        pagePath: 'pages/index/index',
        text: '首页'
      },
      {
        pagePath: 'pages/market/index',
        text: '行情'
      },
      {
        pagePath: 'pages/portfolio/index',
        text: '组合'
      },
      {
        pagePath: 'pages/profile/index',
        text: '我的'
      }
    ]
  }
})
