# WealthOS v2.0 🚀

A modern financial analysis and investment platform with real-time Bitcoin price tracking.

## 🏗️ Modern Tech Stack

### Frontend

- **Vite 6.3** - Lightning fast build tool
- **React 19** - Latest React with new features
- **Tailwind CSS 4.1** - Latest styling framework
- **Shadcn UI** - Modern component library
- **TanStack React Query** - Server state management
- **Recharts** - Beautiful charts for data visualization
- **Zustand** - Lightweight state management

### Backend

- **Python 3.12** - Latest Python
- **FastAPI** - Modern async API framework
- **uv** - Fast Python package manager
- **Binance API** - Real-time cryptocurrency data
- **PostgreSQL** - Database (future)

## 🚀 Quick Start (Recommended)

### 🎭 Mock API Mode (Default)

Perfect for frontend development and testing:

```bash
# 1. Start Mock API Server
python mock_api_server.py

# 2. Start Frontend (in new terminal)
cd frontend
pnpm install
pnpm dev

# 3. Check Status
python status.py
```

**URLs:**

- Frontend: <http://localhost:5173>
- Mock API: <http://localhost:8002>

### 🔗 Real Backend Mode (Optional)

For live Bitcoin data with Redis cache:

```bash
# 1. Start Redis
brew install redis && brew services start redis

# 2. Start Real Backend
cd backend && uv run uvicorn app.main:app --reload --port 8001

# 3. Switch to Real API
# Edit frontend/src/config/api.ts:
# export const CURRENT_MODE: ApiMode = 'REAL'
```

## 📊 Features

### Market Tab

- **Real-time Bitcoin Price Chart** - Live BTC/USD pricing
- **24h Price History** - Simulated historical data
- **Price Statistics** - High, low, and change indicators
- **Auto-refresh** - Updates every 30 seconds

### Dashboard

- Portfolio overview
- Performance metrics
- Quick stats

### Portfolio

- Asset allocation visualization
- Transaction history
- Rebalancing tools

### Analytics

- Performance metrics
- Risk analysis
- Export capabilities

## 🛠️ Development

### Running Both Services

```bash
# Terminal 1 - Backend
cd backend && source .venv/bin/activate.fish && python main.py

# Terminal 2 - Frontend  
cd frontend && pnpm dev
```

### API Endpoints

- `GET /` - API status
- `GET /health` - Health check
- `GET /api/v1/price/{base_asset}/{quote_currency}` - Get price data

## 📈 Bitcoin Chart Integration

The Market tab features a real-time Bitcoin price chart that:

1. Fetches live data from your WealthOS backend
2. Displays 24h price history with beautiful line charts
3. Shows price statistics and change indicators
4. Auto-refreshes every 30 seconds
5. Gracefully handles connection errors

## 🎨 Design System

Built with modern design principles:

- **Clean Interface** - Minimal and intuitive
- **Dark/Light Mode Ready** - CSS variables for theming
- **Responsive Design** - Mobile-first approach
- **Smooth Animations** - Subtle hover effects and transitions

## 🔧 Configuration

### Environment Variables

```env
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/wealthos
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key

# Frontend
VITE_API_URL=http://localhost:8000
```

## 📦 Package Management

- **Backend**: Use `uv` commands only (never `pip`)
- **Frontend**: Use `pnpm` for all package operations

## 🚦 Status

✅ Frontend: Modern Vite + React 19 + Tailwind CSS 4.1  
✅ Backend: FastAPI with Bitcoin price API  
✅ Bitcoin Chart: Real-time data visualization  
✅ CORS: Properly configured for development  

Ready for development! 🎉
