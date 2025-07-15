# Simplified Advisory Architecture

## Overview
Clean, simple workflow: Image → Holdings → Analysis → Personalized Advice

## Components

### 1. Client Schema (replaces IPS)
```
Client {
  personal_info: { name, age, profession, ... }
  risk_profile: { willingness, ability, tolerance }
  financial_goals: { return_target, time_horizon, ... }
  asset_history: [
    { timestamp, portfolio_snapshot, source }
  ]
  constraints: { liquidity_needs, legal_restrictions, ... }
}
```

### 2. Workflow Flow
```
Image → image_analysis.py → Holdings JSON
Holdings JSON + Client + Advisor Character → fund_advisory.py → Advice
```

### 3. fund_advisory.py Simplified
```python
async def generate_advice(
    holdings_data: dict,
    client: Client,
    advisor_character: CharacterConfig
) -> str:
    # 1. Calculate all metrics (portfolio_analysis.py)
    # 2. Build system prompt (client + character)
    # 3. Generate response (LLM)
```

### 4. All Math in portfolio_analysis.py
- Risk level mapping (volatility → risk_level)
- Portfolio metrics calculation
- Asset allocation analysis
- Diversification scoring

## API Flow
1. **POST /analyze-image** → Holdings JSON
2. **POST /generate-advice** (holdings + client + character) → Advice

## Benefits
- Single responsibility per component
- Clear data flow
- Easy to test and maintain
- Modular design 