import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Tabs, TabsList, TabsTrigger, TabsContent } from './components/ui/tabs'
import BitcoinChart from './components/BitcoinChart'
import FundAnalysis from './components/FundAnalysis'
import FundAdvisorDashboard from './components/fundAdvisor/FundAdvisorDashboard'
import InvestmentSimulator from './components/InvestmentSimulator' 
import ErrorBoundary from './components/ErrorBoundary'

const queryClient = new QueryClient()

function App() {
  const [activeTab, setActiveTab] = useState('market');

  return (
    <ErrorBoundary>
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
              <TabsList className="grid w-full grid-cols-7 bg-white/80 backdrop-blur-sm rounded-2xl p-1.5 shadow-lg border border-slate-200/60">
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
                value="fund-advisor" 
                className="flex items-center space-x-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-indigo-500 data-[state=active]:to-indigo-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-200 rounded-xl"
              >
                <span className="text-lg">🎯</span>
                <span className="font-semibold">Fund Advisor</span>
              </TabsTrigger>
              <TabsTrigger 
                  value="investment-simulator" 
                  className="flex items-center space-x-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500 data-[state=active]:to-cyan-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-200 rounded-xl"
                >
                  <span className="text-lg">⏳</span>
                  <span className="font-semibold">Simulator</span>
                </TabsTrigger>
              <TabsTrigger 
                value="fund-analysis" 
                className="flex items-center space-x-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-pink-500 data-[state=active]:to-pink-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-200 rounded-xl"
              >
                <span className="text-lg">🤖</span>
                <span className="font-semibold">AI Analysis</span>
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
                  <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-2xl border border-blue-200">
                      <div className="text-blue-600 text-3xl mb-2">💰</div>
                      <h3 className="font-semibold text-blue-900 mb-1">Total Assets</h3>
                      <p className="text-blue-700 text-sm">Track your investment portfolio value</p>
                    </div>
                    <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-2xl border border-green-200">
                      <div className="text-green-600 text-3xl mb-2">📈</div>
                      <h3 className="font-semibold text-green-900 mb-1">Performance</h3>
                      <p className="text-green-700 text-sm">Monitor returns and growth metrics</p>
                    </div>
                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-2xl border border-purple-200">
                      <div className="text-purple-600 text-3xl mb-2">🎯</div>
                      <h3 className="font-semibold text-purple-900 mb-1">Goals</h3>
                      <p className="text-purple-700 text-sm">Progress towards financial objectives</p>
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
                      <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-4 py-2 rounded-full text-sm font-semibold shadow-lg">
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
                  <div className="relative mb-8">
                    <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-purple-600 rounded-3xl flex items-center justify-center mx-auto shadow-xl">
                      <span className="text-white text-4xl">💼</span>
                    </div>
                    <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-yellow-400 to-yellow-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-xs">⚡</span>
                    </div>
                  </div>
                  <h2 className="text-4xl font-bold text-slate-900 mb-4">Portfolio Management</h2>
                  <p className="text-slate-600 max-w-md mx-auto text-lg leading-relaxed">
                    Advanced portfolio analytics, risk assessment, and optimization tools powered by AI.
                  </p>
                  <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-2xl border border-purple-200">
                      <div className="text-purple-600 text-3xl mb-2">⚖️</div>
                      <h3 className="font-semibold text-purple-900 mb-1">Risk Analysis</h3>
                      <p className="text-purple-700 text-sm">Comprehensive risk metrics and stress testing</p>
                    </div>
                    <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 p-6 rounded-2xl border border-indigo-200">
                      <div className="text-indigo-600 text-3xl mb-2">🔄</div>
                      <h3 className="font-semibold text-indigo-900 mb-1">Rebalancing</h3>
                      <p className="text-indigo-700 text-sm">Smart allocation recommendations</p>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="fund-advisor" className="space-y-8">
                <FundAdvisorDashboard />
              </TabsContent>

              <TabsContent value="investment-simulator" className="space-y-8">
                <InvestmentSimulator />
              </TabsContent>

              <TabsContent value="fund-analysis" className="space-y-8">
                <FundAnalysis />
              </TabsContent>

              <TabsContent value="analytics" className="space-y-8">
                <div className="text-center py-16">
                  <div className="relative mb-8">
                    <div className="w-24 h-24 bg-gradient-to-br from-orange-500 to-orange-600 rounded-3xl flex items-center justify-center mx-auto shadow-xl">
                      <span className="text-white text-4xl">📈</span>
                    </div>
                    <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-cyan-400 to-cyan-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-xs">🔥</span>
                    </div>
                  </div>
                  <h2 className="text-4xl font-bold text-slate-900 mb-4">Advanced Analytics</h2>
                  <p className="text-slate-600 max-w-md mx-auto text-lg leading-relaxed">
                    Deep insights into market trends, factor analysis, and predictive modeling for smarter investment decisions.
                  </p>
                  <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                    <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-2xl border border-orange-200">
                      <div className="text-orange-600 text-3xl mb-2">🎯</div>
                      <h3 className="font-semibold text-orange-900 mb-1">Factor Analysis</h3>
                      <p className="text-orange-700 text-sm">Barra risk model insights</p>
                    </div>
                    <div className="bg-gradient-to-br from-red-50 to-red-100 p-6 rounded-2xl border border-red-200">
                      <div className="text-red-600 text-3xl mb-2">🔮</div>
                      <h3 className="font-semibold text-red-900 mb-1">Predictions</h3>
                      <p className="text-red-700 text-sm">AI-powered forecasting</p>
                    </div>
                    <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 p-6 rounded-2xl border border-cyan-200">
                      <div className="text-cyan-600 text-3xl mb-2">🌊</div>
                      <h3 className="font-semibold text-cyan-900 mb-1">Market Sentiment</h3>
                      <p className="text-cyan-700 text-sm">Real-time sentiment analysis</p>
                    </div>
                  </div>
                </div>
              </TabsContent>
              </div>
            </Tabs>
          </main>

          <footer className="bg-white/70 backdrop-blur-xl border-t border-slate-200/60 mt-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
              <div className="flex justify-between items-center">
                <p className="text-slate-500 text-sm">© 2024 WealthOS. Built with React 19 + Tailwind CSS + AI Analysis</p>
                <div className="flex items-center space-x-4">
                  <span className="text-xs font-semibold text-slate-600">Latest Stack:</span>
                  <div className="flex items-center space-x-3 text-xs">
                    <span className="bg-slate-100 text-slate-600 px-2 py-1 rounded-md">Vite 6.3</span>
                    <span className="bg-slate-100 text-slate-600 px-2 py-1 rounded-md">React 19</span>
                    <span className="bg-slate-100 text-slate-600 px-2 py-1 rounded-md">Tailwind 4.1</span>
                  </div>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
