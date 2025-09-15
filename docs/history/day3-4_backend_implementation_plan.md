# Day 3-4 Backend Implementation Plan

## Overview
This document outlines the implementation plan for Week 1, Day 3-4 of the WealthOS MVP development, focusing on backend API development for fund screenshot analysis and investment advisory workflows.

## Goals
1. **Image Upload & LLM Vision Analysis**: Build FastAPI endpoint to process fund screenshot uploads and extract fund holdings using GPT-4 Vision
2. **LangGraph Workflow System**: Create a reusable LangGraph workflow infrastructure for fund investment advisory
3. **Investment Advisory Logic**: Implement basic investment advisory workflows with risk analysis and recommendations

## Technical Requirements

### 1. Dependencies to Add
We need to add the following dependencies to `backend/pyproject.toml`:
- `langgraph>=0.2.74` - For workflow management
- `langchain-core>=0.3.0` - Core LangChain functionality
- `langchain-openai>=0.2.0` - OpenAI integration
- `pillow>=10.0.0` - Image processing
- `python-multipart>=0.0.9` - File upload handling (already present)
- `openai>=1.0.0` - OpenAI API client

### 2. Project Structure Extensions
```
backend/app/
├── workflows/                 # LangGraph workflows
│   ├── __init__.py
│   ├── base.py               # Base workflow classes
│   ├── fund_advisor.py       # Fund advisory workflow
│   └── image_analysis.py     # Image analysis workflow
├── services/
│   ├── llm_service.py        # LLM integration service
│   ├── image_service.py      # Image processing service
│   └── advisory_service.py   # Investment advisory service
├── schemas/
│   ├── funds.py              # Fund-related schemas
│   ├── advisory.py           # Advisory-related schemas
│   └── uploads.py            # File upload schemas
├── api/routes/
│   ├── funds.py              # Fund analysis endpoints
│   └── advisory.py           # Advisory endpoints
└── models/
    ├── funds.py              # Fund data models
    └── advisory.py           # Advisory data models
```

## Implementation Details

### Phase 1: Core Infrastructure (Day 3 Morning)

#### 1.1 Add Dependencies
Update `pyproject.toml` with required packages and run `uv sync`.

#### 1.2 LLM Service Setup
Create `app/services/llm_service.py`:
- OpenAI GPT-4 Vision integration
- Structured output parsing
- Error handling and retries
- Rate limiting awareness

#### 1.3 Base Workflow Infrastructure
Create `app/workflows/base.py`:
- Abstract base workflow class
- Common workflow patterns
- Checkpointing and state management
- Error handling

### Phase 2: Image Analysis Workflow (Day 3 Afternoon)

#### 2.1 Image Processing Service
Create `app/services/image_service.py`:
- Image validation and preprocessing
- Format conversion (if needed)
- Size optimization
- Error handling

#### 2.2 Fund Holdings Extraction Workflow
Create `app/workflows/image_analysis.py`:
- LangGraph workflow for fund screenshot analysis
- GPT-4 Vision integration
- Structured output parsing for fund holdings
- Error handling and validation

#### 2.3 API Endpoint
Create `app/api/routes/funds.py`:
- POST `/api/funds/analyze-screenshot` endpoint
- File upload handling
- Workflow execution
- Response formatting

### Phase 3: Investment Advisory Workflow (Day 4 Morning)

#### 3.1 Advisory Service
Create `app/services/advisory_service.py`:
- Risk analysis calculations
- Portfolio diversification analysis
- Industry/sector concentration analysis
- Performance metrics

#### 3.2 Fund Advisory Workflow
Create `app/workflows/fund_advisor.py`:
- LangGraph workflow for investment advisory
- Multi-step analysis process
- Risk assessment
- Recommendation generation

#### 3.3 Investment Principles & Prompts
Define core investment principles:
- Risk diversification principles
- Asset allocation guidelines
- Industry concentration limits
- Quality metrics evaluation

### Phase 4: API Integration & Testing (Day 4 Afternoon)

#### 4.1 Advisory API Endpoints
Create `app/api/routes/advisory.py`:
- POST `/api/advisory/analyze-portfolio` endpoint
- GET `/api/advisory/recommendations/{analysis_id}` endpoint
- Workflow status tracking

#### 4.2 Data Models & Schemas
Create comprehensive schemas for:
- Fund holdings data
- Risk analysis results
- Advisory recommendations
- Workflow states

#### 4.3 Integration Testing
- End-to-end workflow testing
- API endpoint testing
- Error handling validation
- Performance benchmarking

## Data Structures

### Fund Holdings Schema
```python
class FundHolding(BaseModel):
    fund_name: str
    fund_code: str
    allocation_percentage: float
    fund_type: str  # equity, bond, hybrid, etc.
    risk_level: str  # low, medium, high
    industry_focus: Optional[str]
    geographic_focus: Optional[str]

class FundPortfolio(BaseModel):
    holdings: List[FundHolding]
    total_value: Optional[float]
    currency: str = "CNY"
    analysis_date: datetime
```

### Advisory Analysis Schema
```python
class RiskAnalysis(BaseModel):
    overall_risk_score: float  # 1-10 scale
    diversification_score: float  # 1-10 scale
    industry_concentration: Dict[str, float]
    geographic_concentration: Dict[str, float]
    risk_factors: List[str]

class AdvisoryRecommendation(BaseModel):
    recommendation_type: str  # rebalance, reduce_risk, increase_diversification
    priority: str  # high, medium, low
    description: str
    suggested_actions: List[str]
    expected_impact: str

class AdvisoryResult(BaseModel):
    portfolio_id: str
    risk_analysis: RiskAnalysis
    recommendations: List[AdvisoryRecommendation]
    overall_score: float
    analysis_timestamp: datetime
```

## LangGraph Workflow Design

### 1. Image Analysis Workflow
```
START → Image Validation → GPT-4 Vision Analysis → Data Extraction → Validation → END
```

### 2. Fund Advisory Workflow
```
START → Portfolio Analysis → Risk Assessment → Diversification Check → Industry Analysis → Recommendation Generation → END
```

### 3. Workflow State Management
- Use MemorySaver for checkpointing
- Implement error recovery
- Support workflow resumption
- Track analysis progress

## Investment Advisory Principles

### Core Principles
1. **Diversification**: No single fund should exceed 20% of portfolio
2. **Risk Balance**: Mix of low, medium, and high-risk funds
3. **Industry Spread**: No single industry should exceed 30% allocation
4. **Geographic Diversification**: Consider domestic vs international exposure
5. **Cost Efficiency**: Prefer funds with reasonable expense ratios

### Risk Assessment Criteria
- **Volatility Analysis**: Historical price movements
- **Correlation Analysis**: Fund correlation with market indices
- **Concentration Risk**: Single security/sector exposure
- **Liquidity Risk**: Fund size and trading volume
- **Manager Risk**: Fund management quality and stability

## API Endpoints Specification

### 1. Fund Screenshot Analysis
```
POST /api/funds/analyze-screenshot
Content-Type: multipart/form-data

Request:
- file: image file (PNG, JPG, JPEG)
- user_id: string (optional)

Response:
{
  "analysis_id": "uuid",
  "status": "completed|processing|failed",
  "portfolio": FundPortfolio,
  "confidence_score": 0.95,
  "processing_time": 1.2
}
```

### 2. Portfolio Advisory Analysis
```
POST /api/advisory/analyze-portfolio
Content-Type: application/json

Request:
{
  "portfolio": FundPortfolio,
  "user_preferences": {
    "risk_tolerance": "medium",
    "investment_horizon": "long_term",
    "goals": ["growth", "income"]
  }
}

Response:
{
  "analysis_id": "uuid",
  "status": "completed|processing|failed",
  "result": AdvisoryResult
}
```

## Error Handling Strategy

### 1. Image Processing Errors
- Invalid file format
- File size limits
- Corrupted images
- Unsupported content

### 2. LLM Analysis Errors
- API rate limits
- Model availability
- Parsing failures
- Confidence thresholds

### 3. Workflow Errors
- State corruption
- Timeout handling
- Resource exhaustion
- External service failures

## Testing Strategy

### 1. Unit Tests
- Individual workflow components
- Service layer functions
- Data validation
- Error handling

### 2. Integration Tests
- End-to-end workflows
- API endpoint testing
- Database interactions
- External service mocking

### 3. Performance Tests
- Image processing speed
- LLM response times
- Workflow execution time
- Concurrent request handling

## Success Metrics

### Day 3 Success Criteria
- [ ] Image upload endpoint working
- [ ] GPT-4 Vision integration functional
- [ ] Fund holdings extraction accurate (>80% confidence)
- [ ] Basic workflow infrastructure in place

### Day 4 Success Criteria
- [ ] Investment advisory workflow operational
- [ ] Risk analysis calculations working
- [ ] Recommendation generation functional
- [ ] API endpoints responding correctly
- [ ] End-to-end testing complete

## Next Steps (Day 5-7)
- Frontend integration
- UI/UX implementation
- Advanced advisory features
- Performance optimization
- User testing preparation

## Notes
- Focus on MVP functionality first
- Implement comprehensive error handling
- Ensure scalable architecture
- Document all APIs thoroughly
- Plan for future workflow additions 