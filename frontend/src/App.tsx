import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Tabs, TabsList, TabsTrigger, TabsContent } from './components/ui/tabs'
import BitcoinChart from './components/BitcoinChart'

const queryClient = new QueryClient()

function App() {
  const [activeTab, setActiveTab] = useState('market');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
        {/* Header */}
        <header className="bg-white/70 backdrop-blur-xl border-b border-slate-200/60 sticky top-0 z-10 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <span className="text-white font-bold text-lg">₿</span>
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-900 via-indigo-900 to-purple-900 bg-clip-text text-transparent">
                      WealthOS
                    </h1>
                    <p className="text-sm text-slate-500 -mt-1 font-medium">Financial Intelligence Platform</p>
                  </div>
                </div>
              </div>
              <button className="flex items-center space-x-2 px-4 py-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-all duration-200 group">
                <span className="text-lg group-hover:rotate-12 transition-transform duration-200">⚙️</span>
                <span className="font-medium">Settings</span>
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-4 bg-white/80 backdrop-blur-sm rounded-2xl p-1.5 shadow-lg border border-slate-200/60">
              <TabsTrigger 
                value="dashboard" 
                className="flex items-center space-x-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-200 rounded-xl"
              >
                <span className="text-lg">🏠</span>
                <span className="font-semibold">Dashboard</span>
              </TabsTrigger>
              <TabsTrigger 
                value="market" 
                className="flex items-center space-x-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-emerald-500 data-[state=active]:to-emerald-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-200 rounded-xl"
              >
                <span className="text-lg">📊</span>
                <span className="font-semibold">Market</span>
              </TabsTrigger>
              <TabsTrigger 
                value="portfolio" 
                className="flex items-center space-x-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-500 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-200 rounded-xl"
              >
                <span className="text-lg">💼</span>
                <span className="font-semibold">Portfolio</span>
              </TabsTrigger>
              <TabsTrigger 
                value="analytics" 
                className="flex items-center space-x-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-orange-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-200 rounded-xl"
              >
                <span className="text-lg">📈</span>
                <span className="font-semibold">Analytics</span>
              </TabsTrigger>
            </TabsList>

            <div className="mt-8">
              <TabsContent value="dashboard" className="space-y-8">
                <div className="text-center py-16">
                  <div className="relative mb-8">
                    <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-blue-600 rounded-3xl flex items-center justify-center mx-auto shadow-xl">
                      <span className="text-white text-4xl">🏠</span>
                    </div>
                    <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-green-400 to-green-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-xs">✓</span>
                    </div>
                  </div>
                  <h2 className="text-4xl font-bold text-slate-900 mb-4">Portfolio Dashboard</h2>
                  <p className="text-slate-600 max-w-md mx-auto text-lg leading-relaxed">
                    Your comprehensive financial overview and performance insights at a glance.
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 max-w-4xl mx-auto">
                    <div className="group bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-slate-200/60 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200">
                        <span className="text-white text-xl">💰</span>
                      </div>
                      <h3 className="font-bold text-slate-900 mb-2 text-lg">Total Portfolio</h3>
                      <p className="text-3xl font-bold text-emerald-600 mb-1">$125,430.50</p>
                      <p className="text-sm text-slate-500">+12.5% this month</p>
                    </div>
                    <div className="group bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-slate-200/60 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200">
                        <span className="text-white text-xl">📈</span>
                      </div>
                      <h3 className="font-bold text-slate-900 mb-2 text-lg">24h Change</h3>
                      <p className="text-3xl font-bold text-blue-600 mb-1">+2.4%</p>
                      <p className="text-sm text-slate-500">+$3,010.33</p>
                    </div>
                    <div className="group bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-slate-200/60 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                      <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200">
                        <span className="text-white text-xl">🎯</span>
                      </div>
                      <h3 className="font-bold text-slate-900 mb-2 text-lg">Total Profit</h3>
                      <p className="text-3xl font-bold text-purple-600 mb-1">$12,430.50</p>
                      <p className="text-sm text-slate-500">+9.9% return</p>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="market" className="space-y-8">
                <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-xl border border-slate-200/60">
                  <div className="flex items-center justify-between mb-8">
                    <div>
                      <h2 className="text-4xl font-bold bg-gradient-to-r from-slate-900 via-emerald-800 to-emerald-700 bg-clip-text text-transparent mb-2">
                        Live Market Data
                      </h2>
                      <p className="text-slate-600 text-lg">Real-time cryptocurrency prices and analytics</p>
                    </div>
                    <div className="text-right">
                      <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-emergreen-500 to-emerald-600 text-white px-4 py-2 rounded-full text-sm font-semibold shadow-lg">
                        <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
                        <span>Live Data</span>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">Powered by CoinGecko API</p>
                    </div>
                  </div>
                  <BitcoinChart />
                </div>
              </TabsContent>

              <TabsContent value="portfolio" className="space-y-8">
                <div className="text-center py-16">
                  <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-purple-600 rounded-3xl flex items-center justify-center mx-auto shadow-xl mb-8">
                    <span className="text-white text-4xl">💼</span>
                  </div>
                  <h2 className="text-4xl font-bold text-slate-900 mb-4">Investment Portfolio</h2>
                  <p className="text-slate-600 max-w-md mx-auto text-lg leading-relaxed">
                    Manage your investments, view asset allocation, and track performance metrics.
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12 max-w-5xl mx-auto">
                    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-slate-200/60">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-bold text-slate-900">Asset Allocation</h3>
                        <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center">
                          <span className="text-white text-sm">📊</span>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div className="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
                          <div className="flex items-center space-x-3">
                            <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                            <span className="text-slate-700 font-medium">Bitcoin (BTC)</span>
                          </div>
                          <span className="font-bold text-slate-900">45%</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
                          <div className="flex items-center space-x-3">
                            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                            <span className="text-slate-700 font-medium">Ethereum (ETH)</span>
                          </div>
                          <span className="font-bold text-slate-900">30%</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
                          <div className="flex items-center space-x-3">
                            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                            <span className="text-slate-700 font-medium">Stocks</span>
                          </div>
                          <span className="font-bold text-slate-900">25%</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-slate-200/60">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-bold text-slate-900">Recent Activity</h3>
                        <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center">
                          <span className="text-white text-sm">📈</span>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div className="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                              <span className="text-green-600 text-xs">+</span>
                            </div>
                            <span className="text-slate-700 font-medium">Buy BTC</span>
                          </div>
                          <span className="font-bold text-green-600">+0.01 BTC</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                              <span className="text-red-600 text-xs">-</span>
                            </div>
                            <span className="text-slate-700 font-medium">Sell ETH</span>
                          </div>
                          <span className="font-bold text-red-600">-0.5 ETH</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-blue-600 text-xs">+</span>
                            </div>
                            <span className="text-slate-700 font-medium">Buy AAPL</span>
                          </div>
                          <span className="font-bold text-blue-600">+10 shares</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="analytics" className="space-y-8">
                <div className="text-center py-16">
                  <div className="w-24 h-24 bg-gradient-to-br from-orange-500 to-orange-600 rounded-3xl flex items-center justify-center mx-auto shadow-xl mb-8">
                    <span className="text-white text-4xl">📊</span>
                  </div>
                  <h2 className="text-4xl font-bold text-slate-900 mb-4">Advanced Analytics</h2>
                  <p className="text-slate-600 max-w-md mx-auto text-lg leading-relaxed">
                    Deep insights, risk metrics, and performance analytics for informed decision making.
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 max-w-6xl mx-auto">
                    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-slate-200/60 hover:shadow-xl transition-all duration-300">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mb-4">
                        <span className="text-white text-xl">📊</span>
                      </div>
                      <h3 className="font-bold text-slate-900 mb-2 text-lg">Sharpe Ratio</h3>
                      <p className="text-3xl font-bold text-blue-600 mb-1">1.45</p>
                      <p className="text-sm text-slate-500">Excellent risk-adjusted return</p>
                    </div>
                    
                    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-slate-200/60 hover:shadow-xl transition-all duration-300">
                      <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-2xl flex items-center justify-center mb-4">
                        <span className="text-white text-xl">📉</span>
                      </div>
                      <h3 className="font-bold text-slate-900 mb-2 text-lg">Max Drawdown</h3>
                      <p className="text-3xl font-bold text-red-600 mb-1">-12.3%</p>
                      <p className="text-sm text-slate-500">Largest peak-to-trough decline</p>
                    </div>
                    
                    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-slate-200/60 hover:shadow-xl transition-all duration-300">
                      <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4">
                        <span className="text-white text-xl">⚡</span>
                      </div>
                      <h3 className="font-bold text-slate-900 mb-2 text-lg">Beta</h3>
                      <p className="text-3xl font-bold text-purple-600 mb-1">0.85</p>
                      <p className="text-sm text-slate-500">Lower market correlation</p>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </div>
          </Tabs>
        </main>

        {/* Footer */}
        <footer className="bg-white/50 backdrop-blur-sm border-t border-slate-200/60 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
              <p className="text-slate-600">
                © 2024 WealthOS. Built with React 19 + Tailwind CSS + CoinGecko API
              </p>
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-4 text-sm text-slate-500">
                  <span className="font-medium">Latest Stack:</span>
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-1 bg-slate-100 rounded-md text-xs font-medium">Vite 6.3</span>
                    <span className="px-2 py-1 bg-slate-100 rounded-md text-xs font-medium">React 19</span>
                    <span className="px-2 py-1 bg-slate-100 rounded-md text-xs font-medium">Tailwind 4.1</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </QueryClientProvider>
  );
}

export default App;
