import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import BitcoinChart from '@/components/BitcoinChart'
import { TrendingUp, PieChart, Settings, Home } from 'lucide-react'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background">
        <header className="border-b bg-card">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-8 w-8 text-primary" />
                  <h1 className="text-2xl font-bold">WealthOS</h1>
                </div>
                <span className="text-sm text-muted-foreground bg-secondary px-2 py-1 rounded">
                  v2.0 - Vite + React 19
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm">
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </Button>
              </div>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          <Tabs defaultValue="market" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="dashboard" className="flex items-center space-x-2">
                <Home className="h-4 w-4" />
                <span>Dashboard</span>
              </TabsTrigger>
              <TabsTrigger value="market" className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4" />
                <span>Market</span>
              </TabsTrigger>
              <TabsTrigger value="portfolio" className="flex items-center space-x-2">
                <PieChart className="h-4 w-4" />
                <span>Portfolio</span>
              </TabsTrigger>
              <TabsTrigger value="analytics" className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4" />
                <span>Analytics</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="dashboard" className="mt-6">
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-3xl font-bold">Dashboard</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="bg-card p-6 rounded-lg border">
                    <h3 className="text-lg font-semibold mb-2">Portfolio Value</h3>
                    <p className="text-3xl font-bold text-green-600">$125,432</p>
                    <p className="text-sm text-muted-foreground">+2.5% from yesterday</p>
                  </div>
                  <div className="bg-card p-6 rounded-lg border">
                    <h3 className="text-lg font-semibold mb-2">Active Positions</h3>
                    <p className="text-3xl font-bold">8</p>
                    <p className="text-sm text-muted-foreground">Across 3 asset classes</p>
                  </div>
                  <div className="bg-card p-6 rounded-lg border">
                    <h3 className="text-lg font-semibold mb-2">Today's P&L</h3>
                    <p className="text-3xl font-bold text-green-600">+$1,248</p>
                    <p className="text-sm text-muted-foreground">+1.02% return</p>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="market" className="mt-6">
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-3xl font-bold">Market Data</h2>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-muted-foreground">
                      Powered by WealthOS Backend
                    </span>
                    <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                  </div>
                </div>
                <BitcoinChart />
              </div>
            </TabsContent>

            <TabsContent value="portfolio" className="mt-6">
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-3xl font-bold">Portfolio</h2>
                  <Button>
                    <PieChart className="h-4 w-4 mr-2" />
                    Rebalance
                  </Button>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-card p-6 rounded-lg border">
                    <h3 className="text-lg font-semibold mb-4">Asset Allocation</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span>Bitcoin (BTC)</span>
                        <span className="font-semibold">35%</span>
                      </div>
                      <div className="w-full bg-secondary rounded-full h-2">
                        <div className="bg-orange-500 h-2 rounded-full" style={{ width: '35%' }}></div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span>Ethereum (ETH)</span>
                        <span className="font-semibold">25%</span>
                      </div>
                      <div className="w-full bg-secondary rounded-full h-2">
                        <div className="bg-blue-500 h-2 rounded-full" style={{ width: '25%' }}></div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span>Stocks</span>
                        <span className="font-semibold">40%</span>
                      </div>
                      <div className="w-full bg-secondary rounded-full h-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{ width: '40%' }}></div>
                      </div>
                    </div>
                  </div>
                  <div className="bg-card p-6 rounded-lg border">
                    <h3 className="text-lg font-semibold mb-4">Recent Transactions</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium">Bought BTC</p>
                          <p className="text-sm text-muted-foreground">0.025 BTC</p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">$2,150</p>
                          <p className="text-sm text-muted-foreground">2 hours ago</p>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium">Sold ETH</p>
                          <p className="text-sm text-muted-foreground">1.5 ETH</p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">$3,280</p>
                          <p className="text-sm text-muted-foreground">Yesterday</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="analytics" className="mt-6">
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-3xl font-bold">Analytics</h2>
                  <Button variant="outline">
                    Export Report
                  </Button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-card p-6 rounded-lg border">
                    <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span>Total Return</span>
                        <span className="font-semibold text-green-600">+24.5%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Sharpe Ratio</span>
                        <span className="font-semibold">1.85</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Max Drawdown</span>
                        <span className="font-semibold text-red-600">-8.2%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Win Rate</span>
                        <span className="font-semibold">68%</span>
                      </div>
                    </div>
                  </div>
                  <div className="bg-card p-6 rounded-lg border">
                    <h3 className="text-lg font-semibold mb-4">Risk Analysis</h3>
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span>Portfolio Beta</span>
                        <span className="font-semibold">0.92</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Volatility</span>
                        <span className="font-semibold">15.3%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>VaR (95%)</span>
                        <span className="font-semibold">$3,247</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Correlation to S&P 500</span>
                        <span className="font-semibold">0.76</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </main>

        <footer className="border-t bg-card mt-12">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                © 2024 WealthOS. Built with Vite + React 19 + Tailwind CSS
              </p>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-muted-foreground">Latest Stack:</span>
                <span className="text-sm bg-secondary px-2 py-1 rounded">Vite 6.3</span>
                <span className="text-sm bg-secondary px-2 py-1 rounded">React 19</span>
                <span className="text-sm bg-secondary px-2 py-1 rounded">Tailwind 4.1</span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </QueryClientProvider>
  )
}

export default App
