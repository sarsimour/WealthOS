# Screenshot Analysis MVP - Development Plan

## 🎯 MVP Overview

**Product:** Portfolio Analysis via Screenshot Upload with Virtual Assistant  
**Timeline:** 8-10 weeks  
**Core Value:** Instantly analyze existing investments through mobile screenshots  

## 🏗️ Technical Architecture

### System Flow
```
User Screenshot → GPT-4 Vision → Fund Recognition → 
Akshare Data Lookup → Risk Analysis → Beautiful Charts → 
Virtual Assistant Explanation
```

### Tech Stack
- **Frontend:** Next.js 15, React, Tailwind, Framer Motion
- **Backend:** FastAPI, Python 3.12
- **AI Services:** GPT-4 Vision, Azure TTS
- **Data:** Akshare (Chinese funds), Redis (caching)
- **Charts:** Chart.js, React Chart.js 2

## 📋 Development Phases

### Phase 1: Foundation (Week 1-2)
**Goal:** Infrastructure + Virtual Assistant

#### Backend Setup
```python
# New API endpoints needed
/api/v1/analysis/
├── upload-screenshot     # Main analysis endpoint
├── fund/{code}          # Fund details lookup  
└── assistant/message    # TTS message generation
```

#### Frontend Components
```tsx
src/components/
├── assistant/
│   ├── VirtualAssistant.tsx
│   ├── AssistantMessage.tsx
│   └── AssistantStates.ts
├── upload/
│   ├── ScreenshotUpload.tsx
│   └── ImagePreview.tsx
└── analysis/
    ├── PortfolioChart.tsx
    ├── RiskMeter.tsx
    └── FundBreakdown.tsx
```

#### Key Services
```python
# backend/app/services/
├── ocr_service.py        # GPT-4 Vision integration
├── fund_lookup_service.py # Akshare data fetching
├── risk_analysis_service.py # Portfolio risk calculation
└── assistant_service.py  # TTS + message generation
```

### Phase 2: Core Analysis Engine (Week 3-4)
**Goal:** Screenshot recognition + fund data lookup

#### OCR Integration
```python
class OCRService:
    async def analyze_screenshot(self, image_bytes) -> List[FundHolding]:
        prompt = """
        Extract Chinese fund information from this screenshot:
        - Fund names (基金名称)
        - Fund codes (基金代码)
        - Current values (市值)
        Return JSON format.
        """
        response = await openai_vision_api(image_bytes, prompt)
        return self.parse_funds(response)
```

#### Fund Data Service
```python
class FundLookupService:
    async def get_fund_details(self, fund_code: str) -> FundDetails:
        # Use akshare for Chinese fund data
        fund_info = ak.fund_open_fund_info_em(fund_code)
        
        # Calculate risk metrics using your Barra factors
        risk_metrics = self.calculate_barra_risk(fund_code)
        
        return FundDetails(
            code=fund_code,
            risk_level=risk_metrics.risk_score,
            max_drawdown=risk_metrics.max_drawdown,
            volatility=risk_metrics.volatility
        )
```

### Phase 3: Virtual Assistant Integration (Week 5-6)
**Goal:** Character states + voice + workflow

#### Assistant Component
```tsx
interface VirtualAssistantProps {
  state: 'welcome' | 'processing' | 'explaining' | 'success';
  message: string;
}

export const VirtualAssistant = ({ state, message }: VirtualAssistantProps) => {
  return (
    <div className="fixed bottom-4 right-4 z-50">
      <img src={`/images/assistant_${state}.png`} className="w-24 h-24" />
      <SpeechBubble message={message} onPlayAudio={() => playTTS(message)} />
    </div>
  );
};
```

#### TTS Integration
```python
class TTSService:
    async def generate_speech(self, text: str) -> str:
        # Azure TTS for Chinese voice
        response = await azure_tts_client.synthesize(
            text=text,
            voice="zh-CN-XiaoxiaoNeural",  # Female Chinese voice
            format="audio-24khz-48kbitrate-mono-mp3"
        )
        return response.audio_url
```

### Phase 4: Visualization + UX (Week 7-8)
**Goal:** Beautiful charts + smooth user experience

#### Chart Components
```tsx
export const PortfolioChart = ({ funds }: { funds: FundHolding[] }) => {
  const data = {
    labels: funds.map(f => f.name),
    datasets: [{
      data: funds.map(f => f.percentage),
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
    }]
  };
  
  return <Pie data={data} options={{ responsive: true }} />;
};

export const RiskMeter = ({ riskScore }: { riskScore: number }) => {
  const color = riskScore > 7 ? 'red' : riskScore > 4 ? 'yellow' : 'green';
  
  return (
    <div className="relative">
      <div className={`h-4 bg-${color}-500 rounded-full transition-all`} 
           style={{ width: `${riskScore * 10}%` }} />
      <p>{riskScore > 7 ? 'High Risk' : 'Medium Risk'}</p>
    </div>
  );
};
```

### Phase 5: Polish + Integration (Week 9-10)
**Goal:** End-to-end flow + error handling

#### Complete User Journey
```tsx
export const AnalysisFlow = () => {
  const [step, setStep] = useState<'welcome' | 'upload' | 'processing' | 'results'>('welcome');
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  
  const handleUpload = async (file: File) => {
    setStep('processing');
    try {
      const result = await analyzeScreenshot(file);
      setAnalysis(result);
      setStep('results');
    } catch (error) {
      // Handle errors gracefully with assistant
      showAssistantMessage('error', 'Let me help you try again!');
    }
  };
  
  return (
    <div>
      {step === 'welcome' && <WelcomeStep />}
      {step === 'upload' && <UploadStep onUpload={handleUpload} />}
      {step === 'processing' && <ProcessingStep />}
      {step === 'results' && <ResultsStep analysis={analysis} />}
      
      <VirtualAssistant 
        state={getAssistantState(step)} 
        message={getAssistantMessage(step, analysis)} 
      />
    </div>
  );
};
```

## 📊 Data Models

```python
class FundHolding(BaseModel):
    fund_code: str
    fund_name: str
    current_value: float
    percentage: float

class RiskMetrics(BaseModel):
    overall_score: int  # 1-10
    volatility: float
    max_drawdown: float
    concentration_risk: int

class PortfolioAnalysis(BaseModel):
    total_value: float
    risk_metrics: RiskMetrics
    funds: List[FundHolding]
    warnings: List[str]
    recommendations: List[str]
```

## 🔧 Key API Endpoints

```python
@router.post("/analysis/upload-screenshot")
async def analyze_screenshot(file: UploadFile):
    # 1. OCR processing
    funds = await ocr_service.extract_funds(file)
    
    # 2. Data lookup
    fund_details = await fund_service.batch_lookup(funds)
    
    # 3. Risk analysis
    analysis = risk_service.analyze_portfolio(fund_details)
    
    # 4. Assistant message
    message = assistant_service.generate_summary(analysis)
    
    return {
        "analysis": analysis,
        "assistant_message": message
    }
```

## 🎨 Assistant Message Examples

```python
ASSISTANT_MESSAGES = {
    'welcome': "Hi! I'm 小美! Let me help you understand your investments. Just upload a screenshot of your fund portfolio!",
    
    'processing': "Great! I'm analyzing your portfolio... 🔍 Reading fund names... 📊 Looking up data... Almost done!",
    
    'high_risk': "Wow! I found {risk_count} high-risk funds. That's like putting all eggs in one basket! Let me show you...",
    
    'results': "Amazing! Your portfolio is worth ¥{total_value:,}. Here's what I discovered about your risk level..."
}
```

## 🚀 Implementation Priority

### Week 1-2: Foundation
- [ ] Setup FastAPI backend structure
- [ ] Create React components for upload
- [ ] Generate character images with AI
- [ ] Basic assistant component

### Week 3-4: Core Logic  
- [ ] GPT-4 Vision integration
- [ ] Akshare fund data service
- [ ] Risk calculation engine
- [ ] Fund recognition testing

### Week 5-6: Assistant Features
- [ ] TTS voice generation
- [ ] Message state management
- [ ] User interaction handling
- [ ] Error state handling

### Week 7-8: Visualization
- [ ] Portfolio charts (pie, bar)
- [ ] Risk meter component
- [ ] Mobile responsive design
- [ ] Chart animations

### Week 9-10: Integration
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Error handling polish
- [ ] Deployment preparation

## 🎯 Success Metrics

- **Technical:** >95% fund recognition, <30s processing
- **UX:** >80% completion rate, >3min engagement
- **Business:** >60% sign-up conversion, >4.5/5 rating

Ready to start building this magical MVP! 🚀 