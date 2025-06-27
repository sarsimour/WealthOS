# 🔧 WealthOS API Configuration Guide

## Quick Start

### 🎭 Using Mock API (Default - Recommended for Testing)

The mock API is **currently active** and provides fake Bitcoin data for frontend testing.

**Current Status:** ✅ **Mock API Active**

- **URL:** <http://localhost:8002>
- **Description:** Mock API with fake data for testing
- **Benefits:** No external dependencies, always available, CORS enabled

### 🔗 Switching to Real Backend

To use real Bitcoin data from CoinGecko/Binance providers:

1. **Update Configuration:**

   ```typescript
   // In frontend/src/config/api.ts
   export const CURRENT_MODE: ApiMode = 'REAL'  // Change from 'MOCK' to 'REAL'
   ```

2. **Start Real Backend:**

   ```bash
   cd backend
   uv run uvicorn app.main:app --reload --port 8001 --host 0.0.0.0
   ```

3. **Verify Real Backend:**

   ```bash
   curl http://localhost:8001/health
   ```

## 📍 Current Configuration

### Active Settings

- **Mode:** MOCK
- **API URL:** <http://localhost:8002/api/v1>
- **Description:** Mock API with fake data for testing

### Available Modes

- **MOCK:** Fake data, no external dependencies, instant response
- **REAL:** Live data from CoinGecko, requires Redis, may have rate limits

## 🚀 Running Services

### Mock API Server (Port 8002)

```bash
python mock_api_server.py
```

- ✅ Always available
- ✅ CORS enabled
- ✅ No rate limits
- ✅ Consistent test data

### Real Backend (Port 8001)

```bash
cd backend && uv run uvicorn app.main:app --reload --port 8001 --host 0.0.0.0
```

- ⚠️ Requires Redis running
- ⚠️ May hit rate limits
- ⚠️ Requires external API keys
- ✅ Real Bitcoin data

### Frontend (Port 5173)

```bash
cd frontend && pnpm dev
```

- ✅ Currently running
- ✅ Configured for mock API
- ✅ Shows API mode in UI

## 🔍 API Endpoints

Both mock and real APIs support the same endpoints:

- `GET /health` - Health check
- `GET /api/v1/prices/crypto/btc` - Current Bitcoin price
- `GET /api/v1/prices/bitcoin/history?period=1d` - Historical data
- `GET /api/v1/prices/bitcoin/full?days=1` - Full Bitcoin data
- `GET /api/v1/cache/stats` - Cache statistics

## 🧪 Testing APIs

Use the provided test script:

```bash
python test_apis.py
```

## 🛠️ Troubleshooting

### Frontend Shows "Failed to fetch"

1. Check if the configured API server is running
2. Verify CORS is enabled on the API server
3. Check browser console for detailed errors

### Real Backend Rate Limited

1. Switch to mock API for testing
2. Wait for rate limit to reset
3. Consider using different data providers

### Redis Connection Failed

1. Install Redis: `brew install redis`
2. Start Redis: `brew services start redis`
3. Verify: `redis-cli ping`

## 📈 Production Deployment

For production, use the real backend with proper configuration:

1. Set up proper Redis instance
2. Configure environment variables
3. Use production-grade data providers
4. Implement proper error handling and rate limiting
