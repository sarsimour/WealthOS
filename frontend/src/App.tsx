import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Tabs, TabsList, TabsTrigger, TabsContent } from './components/ui/tabs'
import BitcoinChart from './components/BitcoinChart'

const queryClient = new QueryClient()

function App() {
  const [activeTab, setActiveTab] = useState('market');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-700 rounded-xl flex items-center justify-center">
                    <span className="text-white font-bold text-lg">📈</span>
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-blue-800 bg-clip-text text-transparent">
                      WealthOS
                    </h1>
                    <p className="text-sm text-gray-500 -mt-1">v2.0 - Vite + React 19</p>
                  </div>
                </div>
              </div>
              <button className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                <span className="text-lg">⚙️</span>
                <span className="font-medium">Settings</span>
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-4 bg-white rounded-xl p-1 shadow-sm border border-gray-200">
              <TabsTrigger 
                value="dashboard" 
                className="flex items-center space-x-2 data-[state=active]:bg-blue-50 data-[state=active]:text-blue-700 data-[state=active]:shadow-sm transition-all"
              >
                <span className="text-lg">🏠</span>
                <span className="font-medium">Dashboard</span>
              </TabsTrigger>
              <TabsTrigger 
                value="market" 
                className="flex items-center space-x-2 data-[state=active]:bg-green-50 data-[state=active]:text-green-700 data-[state=active]:shadow-sm transition-all"
              >
                <span className="text-lg">📊</span>
                <span className="font-medium">Market</span>
              </TabsTrigger>
              <TabsTrigger 
                value="portfolio" 
                className="flex items-center space-x-2 data-[state=active]:bg-purple-50 data-[state=active]:text-purple-700 data-[state=active]:shadow-sm transition-all"
              >
                <span className="text-lg">💼</span>
                <span className="font-medium">Portfolio</span>
              </TabsTrigger>
              <TabsTrigger 
                value="analytics" 
                className="flex items-center space-x-2 data-[state=active]:bg-orange-50 data-[state=active]:text-orange-700 data-[state=active]:shadow-sm transition-all"
              >
                <span className="text-lg">📈</span>
                <span className="font-medium">Analytics</span>
              </TabsTrigger>
            </TabsList>

            <div className="mt-8">
              <TabsContent value="dashboard" className="space-y-6">
                <div className="text-center py-20">
                  <div className="text-6xl mb-4">🏠</div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-4">Dashboard</h2>
                  <p className="text-gray-600 max-w-md mx-auto">
                    Your portfolio overview and performance metrics will be displayed here.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 max-w-4xl mx-auto">
                    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                      <h3 className="font-semibold text-gray-900 mb-2">Total Portfolio</h3>
                      <p className="text-2xl font-bold text-green-600">$125,430.50</p>
                    </div>
                    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                      <h3 className="font-semibold text-gray-900 mb-2">24h Change</h3>
                      <p className="text-2xl font-bold text-blue-600">+2.4%</p>
                    </div>
                    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                      <h3 className="font-semibold text-gray-900 mb-2">Total Profit</h3>
                      <p className="text-2xl font-bold text-purple-600">$12,430.50</p>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="market" className="space-y-6">
                <div className="bg-white rounded-2xl p-1 shadow-sm border border-gray-200">
                  <div className="p-7">
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-green-700 bg-clip-text text-transparent">
                        Market Data
                      </h2>
                      <p className="text-sm text-gray-500 bg-green-50 px-3 py-1 rounded-full border border-green-200">
                        Powered by WealthOS Backend 🚀
                      </p>
                    </div>
                    <BitcoinChart />
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="portfolio" className="space-y-6">
                <div className="text-center py-20">
                  <div className="text-6xl mb-4">💼</div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-4">Portfolio</h2>
                  <p className="text-gray-600 max-w-md mx-auto">
                    Manage your investments, view asset allocation, and track performance.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8 max-w-4xl mx-auto">
                    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                      <h3 className="font-semibold text-gray-900 mb-4">Asset Allocation</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Bitcoin (BTC)</span>
                          <span className="font-medium">45%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Ethereum (ETH)</span>
                          <span className="font-medium">30%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Stocks</span>
                          <span className="font-medium">25%</span>
                        </div>
                      </div>
                    </div>
                    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                      <h3 className="font-semibold text-gray-900 mb-4">Recent Transactions</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Buy BTC</span>
                          <span className="font-medium text-green-600">+0.01 BTC</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Sell ETH</span>
                          <span className="font-medium text-red-600">-0.5 ETH</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Buy AAPL</span>
                          <span className="font-medium text-green-600">+10 shares</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="analytics" className="space-y-6">
                <div className="text-center py-20">
                  <div className="text-6xl mb-4">📊</div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-4">Analytics</h2>
                  <p className="text-gray-600 max-w-md mx-auto">
                    Advanced analytics, risk metrics, and performance insights for your portfolio.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 max-w-6xl mx-auto">
                    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                      <h3 className="font-semibold text-gray-900 mb-2">Sharpe Ratio</h3>
                      <p className="text-2xl font-bold text-blue-600">1.45</p>
                      <p className="text-sm text-gray-500 mt-1">Risk-adjusted return</p>
                    </div>
                    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                      <h3 className="font-semibold text-gray-900 mb-2">Max Drawdown</h3>
                      <p className="text-2xl font-bold text-red-600">-12.3%</p>
                      <p className="text-sm text-gray-500 mt-1">Largest peak-to-trough decline</p>
                    </div>
                    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                      <h3 className="font-semibold text-gray-900 mb-2">Beta</h3>
                      <p className="text-2xl font-bold text-purple-600">0.85</p>
                      <p className="text-sm text-gray-500 mt-1">Market correlation</p>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </div>
          </Tabs>
        </main>

        {/* Footer */}
        <footer className="bg-white/50 backdrop-blur-sm border-t border-gray-200 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
              <p className="text-gray-600">
                © 2024 WealthOS. Built with Vite + React 19 + Tailwind CSS
              </p>
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span className="font-medium">Latest Stack:</span>
                  <div className="flex items-center space-x-2">
                    <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-md font-medium">
                      Vite 6.3
                    </span>
                    <span className="bg-cyan-100 text-cyan-700 px-2 py-1 rounded-md font-medium">
                      React 19
                    </span>
                    <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded-md font-medium">
                      Tailwind 4.1
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </QueryClientProvider>
  )
}

export default App
