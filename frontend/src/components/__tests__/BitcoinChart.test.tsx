import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import BitcoinChart from '../BitcoinChart'

// Mock fetch
global.fetch = jest.fn()

const mockCurrentData = {
  symbol: 'BTC',
  current_price: 45000,
  price_change_24h: 1200,
  price_change_percent_24h: 2.74,
  high_24h: 46000,
  low_24h: 43500,
  historical_data: [
    { timestamp: 1640995200000, price: 44000, volume: 1000000 },
    { timestamp: 1640998800000, price: 44500, volume: 1100000 },
  ],
  currency: 'usd',
  last_updated: '2024-01-01T00:00:00Z'
}

const mockHistoricalData = {
  symbol: 'BTC',
  currency: 'usd',
  period: '7d',
  interval: '2h',
  data: [
    { timestamp: 1640995200000, price: 44000, volume: 1000000 },
    { timestamp: 1640998800000, price: 44500, volume: 1100000 },
    { timestamp: 1641002400000, price: 45000, volume: 1200000 },
  ],
  metadata: {
    total_points: 3,
    start_time: '2024-01-01T00:00:00Z',
    end_time: '2024-01-01T06:00:00Z',
    interval: '2h'
  }
}

describe('BitcoinChart', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear()
  })

  test('renders loading state initially', () => {
    // Mock pending fetch
    (fetch as jest.Mock).mockImplementation(() => new Promise(() => {}))
    
    render(<BitcoinChart />)
    
    expect(screen.getByText('Loading Bitcoin data...')).toBeInTheDocument()
  })

  test('renders error state when fetch fails', async () => {
    // Mock failed fetch
    (fetch as jest.Mock).mockRejectedValue(new Error('Network error'))
    
    render(<BitcoinChart />)
    
    await waitFor(() => {
      expect(screen.getByText('Failed to fetch Bitcoin data')).toBeInTheDocument()
    })
  })

  test('renders Bitcoin data successfully', async () => {
    // Mock successful fetches
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCurrentData)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockHistoricalData)
      })
    
    render(<BitcoinChart />)
    
    await waitFor(() => {
      expect(screen.getByText('Bitcoin (BTC)')).toBeInTheDocument()
    })
    
    // Check if current price is displayed
    expect(screen.getByText('$45,000')).toBeInTheDocument()
    
    // Check if 24h change is displayed
    expect(screen.getByText('+$1,200.00')).toBeInTheDocument()
    expect(screen.getByText('(+2.74%)')).toBeInTheDocument()
    
    // Check if chart title is displayed
    expect(screen.getByText('Bitcoin Price History')).toBeInTheDocument()
  })

  test('allows switching between timeframes', async () => {
    // Mock successful fetches
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCurrentData)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockHistoricalData)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          ...mockHistoricalData,
          period: '1d',
          interval: '15m'
        })
      })
    
    render(<BitcoinChart />)
    
    await waitFor(() => {
      expect(screen.getByText('Bitcoin (BTC)')).toBeInTheDocument()
    })
    
    // Click on 1D timeframe
    const oneDayTab = screen.getByText('1D')
    fireEvent.click(oneDayTab)
    
    // Should fetch 1d data
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/prices/bitcoin/history?period=1d'
      )
    })
  })

  test('displays chart metadata information', async () => {
    // Mock successful fetches
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCurrentData)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockHistoricalData)
      })
    
    render(<BitcoinChart />)
    
    await waitFor(() => {
      expect(screen.getByText('Data Points:')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument()
      expect(screen.getByText('Interval:')).toBeInTheDocument()
      expect(screen.getByText('2h')).toBeInTheDocument()
      expect(screen.getByText('Period:')).toBeInTheDocument()
      expect(screen.getByText('7d')).toBeInTheDocument()
    })
  })

  test('handles retry functionality', async () => {
    // Mock failed then successful fetch
    (fetch as jest.Mock)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockHistoricalData)
      })
    
    render(<BitcoinChart />)
    
    await waitFor(() => {
      expect(screen.getByText('Failed to fetch Bitcoin data')).toBeInTheDocument()
    })
    
    // Click retry button
    const retryButton = screen.getByText('Retry')
    fireEvent.click(retryButton)
    
    // Should attempt to fetch again
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(3) // Initial current + historical + retry
    })
  })

  test('updates current data every 30 seconds', async () => {
    jest.useFakeTimers()
    
    // Mock successful fetches
    const mockFetch = (fetch as jest.Mock);
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockCurrentData)
    })
    
    render(<BitcoinChart />)
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2) // Initial calls
    })
    
    // Fast-forward 30 seconds
    jest.advanceTimersByTime(30000)
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/prices/bitcoin/full?days=1'
      )
    })
    
    jest.useRealTimers()
  })
}) 