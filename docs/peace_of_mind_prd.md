# Peace of Mind Investment Platform - Product Requirements Document v1.0

## Executive Summary

**Project Name:** 省心投 (Peace of Mind Investment)  
**Vision:** Help ordinary investors "lose less money, earn more money" (少亏钱，尽量赚钱)  
**Mission:** Build a behavioral correction tool that works against users' worst investment instincts  

## 1. Product Overview

### 1.1 Product Purpose
Peace of Mind Investment is an anti-behavioral bias investment platform designed to guide retail investors away from common investment mistakes through simplified UI/UX, gamified education, and AI-powered emotional support.

### 1.2 Target Market
- Primary: Retail investors in Chinese markets aged 25-45
- Secondary: Investment beginners with low financial literacy
- Tertiary: Emotional investors prone to panic selling/FOMO buying

### 1.3 Success Metrics
- User retention rate > 80% after 3 months
- Average portfolio volatility reduction > 30% vs individual stock picking
- User education completion rate > 60%
- Customer satisfaction score > 4.5/5
- Cost savings demonstrated to users > ¥5000/year average

## 2. User Persona - "God-Tier User"

### 2.1 Primary Characteristics
- **Very bad temper (脾气非常大)**: Gets angry easily when facing losses or confusing UI
- **Low financial literacy (智商非常低)**: Cannot understand financial jargon, prefers simple visuals
- **Extremely impatient (非常没有耐心)**: Short attention span, demands instant feedback
- **Very cost-conscious (非常非常小气)**: Highly sensitive to fees and costs

### 2.2 User Behaviors
- Prone to emotional trading decisions
- Chases hot stocks and trends
- Panic sells during market downturns
- Focuses on short-term returns over long-term strategy
- Easily overwhelmed by complex financial information

### 2.3 Design Principles
- **Zero friction + Strong reassurance**
- **Zero jargon + Strong analogies**
- **Short paths + Instant feedback**
- **Cost visibility + Value demonstration**

## 3. Functional Requirements

### 3.1 Module 1: Investor Education System - "Wealth Bootcamp" (财富训练营)

#### 3.1.1 Contextual Tips System (场景化Tips系统)
**Purpose:** Deliver timely educational content without interrupting user flow

**Features:**
- **Smart Triggers:** Activate during market volatility, user login, pre-trade confirmation
- **Content Format:** "Golden quotes + Memes/Comics" covering reassurance, warnings, encouragement
- **Delivery Method:** Non-intrusive lightboxes, notification bars, snackbars
- **Emotional Range:** Reassuring, warning, encouraging, calming content

**Technical Requirements:**
- Real-time market data integration for trigger conditions
- Content management system with emotional tagging
- A/B testing framework for message effectiveness
- User preference learning algorithm

#### 3.1.2 Gamified Learning Module (游戏化学习模块)
**Purpose:** Educate users on core investment principles through engaging gameplay

**Features:**
- **Linear Progression:** Level-based system with clear advancement path
- **Content Format:** <60 second animations/videos + 1-2 scenario-based multiple choice questions
- **Reward System:** Virtual badges ("Pitfall Avoider", "Long-term Thinker"), points, achievement tracking
- **Topics:** Diversification, risk management, long-term thinking, emotional control

**Technical Requirements:**
- Video streaming capabilities
- Progress tracking and analytics
- Achievement system with social features
- Adaptive content difficulty based on user performance

### 3.2 Module 2: AI Virtual Investment Advisor - "Personal Chat Companion" (私人陪聊)

#### 3.2.1 AI Persona System
**Purpose:** Provide personalized communication style matching user preferences

**Features:**
- **Persona Options:** 2-3 distinct personalities (e.g., "Blunt Grandpa", "Warm Senior Sister")
- **Consistent Voice:** Maintain character consistency across all interactions
- **Personality Traits:** Unique speech patterns, humor styles, advice approaches

**Technical Requirements:**
- Natural Language Processing for persona consistency
- Conversation history and context management
- Personality profile storage and retrieval

#### 3.2.2 Conversational Risk Assessment
**Purpose:** Assess user risk tolerance through natural conversation

**Features:**
- **Scenario-based Questions:** "If you won ¥500,000, would you buy a house or invest in hot stocks?"
- **Slang Understanding:** Interpret emotional expressions like "亏麻了" (lost big), "求回本" (want to break even)
- **Dynamic Assessment:** Continuously update risk profile based on conversations

**Technical Requirements:**
- Advanced NLP for Chinese slang and emotional expression recognition
- Risk scoring algorithm
- Conversation flow management
- Integration with portfolio recommendation engine

#### 3.2.3 Proactive Engagement System
**Purpose:** Initiate conversations at critical moments for emotional support

**Features:**
- **Market Event Triggers:** High volatility periods, major market news
- **Portfolio Triggers:** Significant drift from target allocation, loss thresholds
- **Scheduled Triggers:** Regular investment reminders, check-ins
- **Emotional Support:** Prioritize validation over data-driven advice

**Technical Requirements:**
- Real-time market monitoring
- Portfolio analysis engine
- Notification system with timing optimization
- Emotional intelligence algorithms

### 3.3 Module 3: Investment Proposals & Reports - "One-Slide PPT" (一图流PPT)

#### 3.3.1 Portfolio Naming & Branding
**Purpose:** Make investment products relatable and goal-oriented

**Features:**
- **Colloquial Names:** "稳稳的幸福" (Steady Happiness), "年轻就要浪" (Young & Bold), "选择困难症" (Decision Paralysis)
- **Goal-Based Categories:** Retirement, growth, conservative, aggressive
- **Visual Branding:** Distinct colors and icons for each portfolio type

#### 3.3.2 Visual-First Reports
**Purpose:** Present complex financial information in PowerPoint-style visuals

**Features:**
- **Performance Simulation:** Smooth upward portfolio curve vs volatile individual stock charts
- **Risk Comparison:** "Maximum possible loss" visualization vs other products
- **Asset Allocation Pie Chart:** "Eggs in different baskets" metaphor visualization
- **Minimal Text:** Focus on visual impact over detailed explanations

**Technical Requirements:**
- Advanced charting and visualization library
- Real-time data for performance simulations
- Mobile-optimized responsive design
- Print-friendly PDF generation

#### 3.3.3 Cost Savings Calculator
**Purpose:** Demonstrate tangible value proposition

**Features:**
- **Fee Comparison:** Platform approach vs self-directed trading
- **Annual Savings Projection:** Quantified cost benefits
- **Real-time Calculation:** Dynamic updates based on portfolio size
- **Prominent Display:** Featured prominently on proposal pages

#### 3.3.4 AI Plain Language Summary
**Purpose:** Provide human-readable interpretation of investment recommendations

**Features:**
- **Key Questions Answered:** "Should I buy it?", "What's the catch?", "What's the upside?"
- **Persona-Consistent Voice:** Match selected AI advisor personality
- **Action-Oriented:** Clear next steps and recommendations

### 3.4 Module 4: Fund Information Tools - "Risk-First Fund Screener" (风险置顶的基金超市)

#### 3.4.1 Risk-First Information Architecture
**Purpose:** Reorient user focus toward risk instead of short-term returns

**Features:**
- **Above-the-Fold Risk Metrics:** Prominent display of max drawdown and volatility
- **Plain Language Risk Explanation:** "This fund's worst drop was XX%. Not for the faint of heart."
- **Secondary Information:** Standard details (manager, holdings, performance) below the fold
- **Risk Color Coding:** Visual hierarchy emphasizing risk levels

#### 3.4.2 Long-Term Performance Focus
**Purpose:** Discourage short-term thinking

**Features:**
- **Default Time Horizons:** 3-year, 5-year, or since-inception performance
- **De-emphasized Short-term:** Minimize 1-month and 3-month returns visibility
- **Historical Context:** Show performance through different market cycles

#### 3.4.3 Risk-Aware Search & Sorting
**Purpose:** Guide users toward risk-conscious decision making

**Features:**
- **Default Sorting:** Risk-based sorting options prioritized
- **High-Risk Warnings:** Automatic warnings for thematic/sector funds
- **Search Query Analysis:** Detect high-risk searches and provide warnings

**Technical Requirements:**
- Fund data aggregation from multiple sources
- Risk calculation algorithms
- Search intent analysis
- Real-time warning system

## 4. Non-Functional Requirements

### 4.1 Performance Requirements
- Page load time < 2 seconds on 4G networks
- 99.9% uptime during market hours
- Support for 100,000+ concurrent users
- Real-time data updates with < 5 second latency

### 4.2 Security Requirements
- Two-factor authentication for account access
- End-to-end encryption for sensitive data
- Compliance with Chinese financial data regulations
- Regular security audits and penetration testing

### 4.3 Usability Requirements
- Mobile-first responsive design
- Accessibility compliance (WCAG 2.1 AA)
- Support for Chinese language with simplified/traditional variants
- Maximum 3-step user flows for core functions

### 4.4 Scalability Requirements
- Horizontal scaling capability
- Microservices architecture
- CDN integration for global content delivery
- Database sharding for large user bases

## 5. Technical Architecture

### 5.1 Backend Requirements
- **Framework:** FastAPI with Python 3.12
- **Database:** PostgreSQL with Redis caching
- **AI/ML:** Integration with large language models for chat functionality
- **Data Sources:** Real-time market data feeds (Chinese markets via akshare)
- **Authentication:** JWT-based with fastapi-users

### 5.2 Frontend Requirements
- **Framework:** Next.js 15 with React 18
- **Styling:** Tailwind CSS with Shadcn UI components
- **State Management:** Zustand for global state, TanStack Query for server state
- **Charts:** Recharts or D3.js for financial visualizations

### 5.3 Mobile Requirements
- Progressive Web App (PWA) capabilities
- Native mobile app for iOS/Android (future phase)
- Offline functionality for core features

## 6. Integration Requirements

### 6.1 Data Sources
- **Chinese Markets:** akshare for A-shares, Hong Kong stocks
- **International Markets:** Yahoo Finance API
- **Cryptocurrency:** Binance API for crypto data
- **Fund Information:** Third-party fund data providers

### 6.2 Third-Party Services
- **Payment Processing:** Alipay, WeChat Pay integration
- **SMS/Email:** Notification services
- **Analytics:** User behavior tracking and analysis
- **Customer Support:** Integrated chat system

## 7. Compliance & Regulatory

### 7.1 Financial Regulations
- Compliance with Chinese Securities Regulatory Commission (CSRC) guidelines
- Investment advisor license requirements
- Data privacy compliance (PIPL - Personal Information Protection Law)

### 7.2 Content Guidelines
- Investment education content review and approval
- Risk disclosure requirements
- Clear fee structure communication

## 8. Success Criteria & KPIs

### 8.1 User Engagement
- Daily Active Users (DAU) growth rate > 5% monthly
- Session duration > 8 minutes average
- Education module completion rate > 60%

### 8.2 Financial Impact
- User portfolio performance improvement vs benchmark
- Cost savings per user > ¥5,000 annually
- Reduced trading frequency (anti-overtrading success)

### 8.3 Business Metrics
- Customer acquisition cost < ¥200
- Lifetime value > ¥2,000
- Churn rate < 5% monthly

## 9. Implementation Phases

### Phase 1: Foundation (3 months)
- Core platform infrastructure
- Basic AI chat functionality
- Simple fund information display
- User authentication and onboarding

### Phase 2: Core Features (3 months)
- Complete education system
- Advanced AI personas
- Portfolio recommendation engine
- Visual reporting system

### Phase 3: Advanced Features (3 months)
- Proactive engagement system
- Advanced analytics and personalization
- Mobile app development
- Third-party integrations

### Phase 4: Scale & Optimize (3 months)
- Performance optimization
- Advanced AI capabilities
- Regulatory compliance
- Market expansion preparation

## 10. Risk Mitigation

### 10.1 Technical Risks
- **AI Reliability:** Implement fallback mechanisms for AI failures
- **Data Quality:** Multiple data source validation
- **Performance:** Load testing and optimization strategies

### 10.2 Business Risks
- **Regulatory Changes:** Compliance monitoring and adaptive architecture
- **Market Volatility:** Stress testing during extreme market conditions
- **User Adoption:** Extensive user testing and feedback integration

### 10.3 Operational Risks
- **Team Scaling:** Clear documentation and knowledge transfer processes
- **Security Breaches:** Comprehensive security protocols and incident response
- **Technology Dependencies:** Vendor diversification and backup systems 