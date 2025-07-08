# Task Plan: Personalized Investment Advisor Enhancement

## Overview
Transform the current technical investment advisor into a more personalized, accessible, and character-driven advisor that speaks to ordinary people in a popular, engaging style.

## Task Breakdown

### 1. Enhanced LLM Service with Character Support
**File:** `backend/app/services/llm_service.py`

**Objective:** Create a flexible character-based advisor service that can use different models and personalities.

**Requirements:**
- Add configurable model parameters (different API keys, base URLs, models)
- Create character schema based on `assistant_character_prompts.md`
- Support customizable talking styles (professional, casual, slightly mean, etc.)
- Separate system prompts for different character personalities
- Make character configuration easily modifiable

**Implementation:**
- New `CharacterAdvisorService` class
- Character schema with personality traits, speaking style, tone
- Template system for character prompts
- Configuration management for multiple LLM providers

### 2. Move Mathematical Computations to Portfolio Analysis
**File:** `backend/app/analysis/fof/portfolio_analysis.py`

**Objective:** Centralize all mathematical computations in the portfolio analysis module.

**Functions to Move/Enhance:**
- `_calculate_portfolio_risk()` → `calculate_portfolio_risk_metrics()`
  - Use real fund NAV history data
  - Calculate historical volatility and covariance
  - Proper annual volatility calculation
  - Risk level classification based on real metrics

- `_calculate_diversification()` → `calculate_diversification_metrics()`
  - Use Barra factor exposure results
  - Check style factor concentration
  - Sector exposure analysis
  - Return comprehensive diversification assessment

**New Functions:**
- `get_fund_historical_data()` - Fetch NAV and return data
- `calculate_correlation_matrix()` - Portfolio correlation analysis
- `assess_factor_concentration()` - Style/sector concentration risks

### 3. Workflow Character Integration
**File:** `backend/app/workflows/fund_advisory.py`

**Objective:** Transform the advisory workflow to use character-based responses.

**Changes:**
- Replace technical language with accessible explanations
- Use character service for personalized responses
- Simplify complex financial concepts
- Add personality-driven commentary
- Make advice more relatable and actionable

**Character Traits to Implement:**
- **Tone:** Slightly sassy but helpful (like a smart friend)
- **Language:** Simple, direct, occasionally playful
- **Style:** Cut through jargon, call out obvious mistakes
- **Personality:** Confident, slightly opinionated, but caring

### 4. Character Configuration System
**File:** `backend/app/schemas/character.py` (new)

**Objective:** Create a flexible character configuration system.

**Schema Elements:**
- Character personality traits
- Speaking style preferences
- Tone modifiers (professional, casual, sassy, etc.)
- Domain-specific knowledge level
- Response templates

### 5. Enhanced Portfolio Analysis Functions
**File:** `backend/app/analysis/fof/portfolio_analysis.py`

**New/Enhanced Functions:**
- Real volatility calculation using historical data
- Factor concentration analysis
- Risk-adjusted return metrics
- Portfolio efficiency scoring
- Sector/style drift detection

## Implementation Priority

### Phase 1: Core Infrastructure
1. Create character schema and configuration system
2. Enhance LLM service with character support
3. Move mathematical functions to portfolio_analysis.py

### Phase 2: Character Integration
1. Implement character-based advisor service
2. Update workflow to use character responses
3. Create personality-driven response templates

### Phase 3: Enhanced Analytics
1. Implement real historical data analysis
2. Add sophisticated diversification metrics
3. Create factor concentration analysis

## Character Personality Design

### Target Persona: "The Smart Friend"
- **Age:** Young professional (25-30)
- **Style:** Direct, honest, slightly sarcastic
- **Approach:** Simplifies complex topics
- **Tone Examples:**
  - "Okay, let's be real about your portfolio..."
  - "This fund is basically doing nothing for you"
  - "Here's what you actually need to know..."
  - "Stop overthinking this - here's the deal"

### Response Style Guidelines
- **Technical → Simple:** "High correlation" → "These funds basically do the same thing"
- **Jargon → Plain:** "Alpha generation" → "Actually beating the market"
- **Formal → Casual:** "We recommend" → "You should probably"
- **Diplomatic → Direct:** "Suboptimal allocation" → "This is a mess, let's fix it"

## Success Metrics
- Character responses feel natural and engaging
- Complex financial concepts explained simply
- Users understand and act on advice
- Advisor feels like a helpful friend, not a robot
- Mathematical accuracy maintained despite simplified language

## Files to Modify
1. `backend/app/services/llm_service.py` - Enhanced service
2. `backend/app/schemas/character.py` - New character schema
3. `backend/app/analysis/fof/portfolio_analysis.py` - Enhanced analytics
4. `backend/app/workflows/fund_advisory.py` - Character integration
5. `backend/app/core/config.py` - Character configuration
6. `backend/test_workflow.py` - Updated tests

## Configuration Files
- Character personality templates
- Response style configurations
- Model provider settings
- Tone and style modifiers 