# Fund of Funds (FOF) Analysis System

A comprehensive system for analyzing Chinese fund portfolios using Barra factor models and relative performance metrics.

## 🎯 Overview

This system provides the foundation for Fund of Funds analysis with the following capabilities:

1. **Data Processing**: Chinese stock/fund code mapping and name normalization
2. **Factor Analysis**: Barra factor data management with mock data generation for testing
3. **Portfolio Analytics**: Portfolio-level factor calculation and relative risk analysis
4. **Performance Metrics**: Comprehensive relative performance analysis vs benchmarks

## 📁 Project Structure

```
backend/
├── app/
│   ├── data/
│   │   ├── code_mapping.py      # Stock/fund code suffix mapping
│   │   ├── name_mapping.py      # Fund name normalization
│   │   ├── fund_data.py         # AKShare integration (with caching)
│   │   └── barra_factors.py     # Barra factor data management
│   └── analysis/
│       └── fof/
│           └── portfolio_analysis.py  # Portfolio factor & performance analysis
├── test_fof_system.py           # Comprehensive system test
└── README_FOF_SYSTEM.md         # This file
```

## 🚀 Key Features

### 1. Code Mapping (`app/data/code_mapping.py`)

Handles Chinese stock exchange code mapping:

- **SSE (Shanghai)**: `.SH` suffix for A-shares (6xxxxx), ETFs (51xxxx), B-shares (9xxxxx)
- **SZSE (Shenzhen)**: `.SZ` suffix for main board (00xxxx), ChiNext (30xxxx), ETFs (159xxx)
- **BSE (Beijing)**: `.BJ` suffix for listed stocks (83xxxx, 87xxxx, 88xxxx, 92xxxx)

```python
from data.code_mapping import add_exchange_suffix

# Automatic suffix detection
add_exchange_suffix("000001")  # → "000001.SZ" (SZSE main board)
add_exchange_suffix("600000")  # → "600000.SH" (SSE A-share)
add_exchange_suffix("300001")  # → "300001.SZ" (SZSE ChiNext)
```

### 2. Name Mapping (`app/data/name_mapping.py`)

Normalizes fund names for better matching between Alipay and AKShare:

```python
from data.name_mapping import normalize_alipay_fund_name, normalize_akshare_fund_name

# Remove parentheses from Alipay names
normalize_alipay_fund_name("华夏成长混合(A类)")  # → "华夏成长混合"

# Remove common suffixes from AKShare names
normalize_akshare_fund_name("华夏成长证券投资基金")  # → "华夏成长"
```

### 3. Barra Factors (`app/data/barra_factors.py`)

Manages Barra factor data with 18 common factors:

- **Size**: SIZE, MIDCAP
- **Value**: BTOP, EARNYLD, RESVOL  
- **Growth**: GROWTH, SGRO
- **Momentum**: RSTR, DASTD, CMRA
- **Leverage**: MLEV, DTOA
- **Liquidity**: STOM, STOQ, STOA
- **Quality**: ATVR, BLEV
- **Beta**: BETA

```python
from data.barra_factors import get_barra_factors

# Generate mock factors for testing
stock_codes = ['000001.SZ', '600000.SH', '300001.SZ']
factors = await get_barra_factors(stock_codes, force_mock=True)
```

### 4. Portfolio Analysis (`app/analysis/fof/portfolio_analysis.py`)

Core FOF analysis functionality:

**Portfolio Factor Calculation**:
```python
from analysis.fof.portfolio_analysis import calculate_portfolio_barra_factors

# Calculate portfolio-level factors from holdings
portfolio_factors = calculate_portfolio_barra_factors(
    holdings_df,      # Fund holdings with weights
    barra_factors_df  # Stock-level factor data
)
```

**Relative Risk Analysis**:
```python
from analysis.fof.portfolio_analysis import calculate_relative_risk_exposure

# Compare portfolio vs benchmark factor exposures
relative_exposure = calculate_relative_risk_exposure(
    portfolio_factors,
    benchmark_factors
)
```

**Performance Metrics**:
```python
from analysis.fof.portfolio_analysis import calculate_relative_performance_metrics

# Comprehensive performance analysis
metrics = calculate_relative_performance_metrics(
    portfolio_returns,
    benchmark_returns
)
# Returns: total_return, excess_return, tracking_error, information_ratio, etc.
```

## 🧪 Testing

Run the comprehensive system test:

```bash
cd backend
python test_fof_system.py
```

This test covers:
1. Code mapping functionality
2. Name normalization
3. Mock Barra factor generation
4. Portfolio factor calculation
5. Relative risk analysis
6. Performance metrics calculation
7. Summary reporting

## 📊 Key Algorithms

### Portfolio Factor Calculation

The core calculation is a matrix multiplication:

```
Portfolio_Factor = Holdings_Weights^T × Stock_Factors
```

Where:
- `Holdings_Weights` is a vector of portfolio weights
- `Stock_Factors` is a matrix of stock-level Barra factors
- Result is a vector of portfolio-level factor exposures

### Relative Risk Exposure

```
Relative_Exposure = Portfolio_Factor - Benchmark_Factor
```

This shows how much the portfolio deviates from the benchmark on each factor.

### Performance Metrics

Key metrics calculated:
- **Tracking Error**: `std(Portfolio_Returns - Benchmark_Returns) × √252`
- **Information Ratio**: `mean(Excess_Returns) / std(Excess_Returns) × √252`
- **Beta**: `cov(Portfolio, Benchmark) / var(Benchmark)`
- **Alpha**: `mean(Excess_Returns) × 252`

## 🔧 Configuration

### Cache Settings

Data is cached in:
- Fund data: `data/cache/funds/`
- Barra factors: `data/cache/barra/`

### Exchange Mapping Rules

The system follows Chinese market conventions:

| Exchange | Code Pattern | Examples | Suffix |
|----------|--------------|----------|--------|
| SSE | 6xxxxx (A-shares), 51xxxx (ETFs), 9xxxxx (B-shares) | 600000, 510050, 900001 | .SH |
| SZSE | 00xxxx (main), 30xxxx (ChiNext), 159xxx (ETFs) | 000001, 300001, 159915 | .SZ |
| BSE | 82xxxx (preferred), 83/87/88/92xxxx (listed) | 920001, 830001 | .BJ |

## 🚀 Next Steps

### Integration with Real Data

1. **AKShare Integration**: Replace mock data with real fund holdings from AKShare
2. **Excel Barra Factors**: Load real Barra factor data from Excel files
3. **Database Storage**: Add PostgreSQL/MongoDB for persistent storage
4. **Redis Caching**: Implement Redis for fast data access

### Performance Optimization

1. **Polars Integration**: Use Polars for faster computation on large datasets
2. **Async Processing**: Batch process multiple funds concurrently
3. **Memory Optimization**: Implement data streaming for large portfolios

### Advanced Analytics

1. **Risk Attribution**: Decompose portfolio risk by factors
2. **Scenario Analysis**: Stress test portfolios under different market conditions
3. **Optimization**: Portfolio construction with factor constraints
4. **Backtesting**: Historical performance analysis

## 📚 Dependencies

Required packages:
```bash
pip install pandas numpy
```

Optional for enhanced performance:
```bash
pip install polars akshare redis
```

## 🤝 Usage Examples

### Basic Workflow

```python
import asyncio
from data.code_mapping import add_exchange_suffix
from data.barra_factors import get_barra_factors
from analysis.fof.portfolio_analysis import calculate_portfolio_barra_factors

async def analyze_fund():
    # 1. Prepare stock codes
    stock_codes = ['000001', '600000', '300001']
    stock_codes_with_suffix = [add_exchange_suffix(code) for code in stock_codes]
    
    # 2. Get Barra factors
    barra_factors = await get_barra_factors(stock_codes_with_suffix, force_mock=True)
    
    # 3. Create mock holdings
    import pandas as pd
    holdings = pd.DataFrame({
        '股票代码_带后缀': stock_codes_with_suffix,
        '占净值比例': [0.4, 0.35, 0.25]
    })
    
    # 4. Calculate portfolio factors
    portfolio_factors = calculate_portfolio_barra_factors(holdings, barra_factors)
    
    print("Portfolio factor exposures:")
    print(portfolio_factors.round(4))

# Run the analysis
asyncio.run(analyze_fund())
```

### Creating Custom Benchmarks

```python
from analysis.fof.portfolio_analysis import create_benchmark_from_funds

# Combine multiple fund holdings into a benchmark (equal-weighted average)
benchmark = create_benchmark_from_funds(
    fund_holdings_list=[fund1_holdings, fund2_holdings, fund3_holdings],
    fund_codes=["fund1", "fund2", "fund3"]  # Fund identifiers
)
# Note: Creates average stock weights across all funds
# Total weight < 1.0 reflects average stock exposure (rest is cash/bonds)
```

## 📈 Output Examples

The system generates comprehensive analysis reports including:

- **Factor Exposure Summary**: Portfolio vs benchmark factor loadings
- **Performance Metrics**: Returns, risk measures, and ratios
- **Risk Analysis**: Factor-based risk decomposition
- **Recommendations**: Actionable insights for portfolio management

## 🎯 Business Value

This system enables:

1. **Risk Management**: Identify and quantify factor exposures
2. **Performance Attribution**: Understand sources of returns
3. **Portfolio Construction**: Build factor-aware portfolios
4. **Compliance**: Monitor adherence to investment mandates
5. **Client Reporting**: Generate professional analysis reports

---

*Built for WealthOS - Advanced Financial Analysis Platform* 