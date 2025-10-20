/**
 * Fund Advisor TypeScript Types
 * Based on backend Pydantic schemas
 */

export enum FundType {
  STOCK = "stock",
  BOND = "bond", 
  MIXED = "mixed",
  INDEX = "index",
  MONEY_MARKET = "money_market",
  QDII = "qdii"
}

export enum AnalysisPeriod {
  ONE_MONTH = "1m",
  THREE_MONTHS = "3m", 
  SIX_MONTHS = "6m",
  ONE_YEAR = "1y",
  TWO_YEARS = "2y",
  THREE_YEARS = "3y",
  FIVE_YEARS = "5y",
  SINCE_INCEPTION = "since_inception"
}

export enum FundStatus {
  NORMAL = "normal",
  SUSPENDED = "suspended",
  CLOSED = "closed"
}

// Basic fund information
export interface Fund {
  fund_code: string;
  fund_name: string;
  fund_type: FundType;
  inception_date: string;
  company_name: string;
  company_code: string;
  total_asset: number;
  total_share: number;
  management_fee: number;
  custodian_fee: number;
  investment_scope: string;
  investment_target: string;
  status: FundStatus;
  benchmark: string;
}

// Fund manager information
export interface FundManager {
  manager_id: string;
  manager_name: string;
  education: string;
  experience_years: number;
  current_funds_count: number;
  total_asset_managed: number;
}

// Fund NAV (Net Asset Value) data
export interface FundNav {
  fund_code: string;
  nav_date: string;
  unit_nav: number;
  accumulated_nav: number;
  adjusted_nav: number;
  purchase_status: string;
  redemption_status: string;
  dividend_per_unit: number;
}

// Fund holdings information  
export interface FundHolding {
  fund_code: string;
  report_date: string;
  stock_code: string;
  stock_name: string;
  holding_ratio: number;
  holding_value: number;
  holding_shares: number;
  sw_l1_industry: string;
  sw_l2_industry: string;
}

// Shenwan industry classification
export interface SwIndustry {
  industry_code: string;
  industry_name: string;
  level: number;
  parent_code?: string;
  description: string;
  is_active: boolean;
}

// Analysis result structures
export interface ReturnAnalysis {
  total_return_1m: number;
  total_return_3m: number;
  total_return_6m: number;
  total_return_1y: number;
  total_return_2y: number;
  total_return_3y: number;
  total_return_5y: number;
  total_return_since_inception: number;
  annualized_return_1y: number;
  annualized_return_2y: number;
  annualized_return_3y: number;
  annualized_return_5y: number;
  annualized_return_since_inception: number;
  excess_return_1m: number;
  excess_return_3m: number;
  excess_return_6m: number;
  excess_return_1y: number;
  category_rank_1m: number;
  category_rank_3m: number;
  category_rank_6m: number;
  category_rank_1y: number;
  category_percentile_1m: number;
  category_percentile_3m: number;
  category_percentile_6m: number;
  category_percentile_1y: number;
}

export interface RiskAnalysis {
  volatility_1y: number;
  volatility_2y: number;
  volatility_3y: number;
  max_drawdown_1y: number;
  max_drawdown_2y: number;
  max_drawdown_3y: number;
  sharpe_ratio_1y: number;
  sharpe_ratio_2y: number;
  sharpe_ratio_3y: number;
  sortino_ratio_1y: number;
  sortino_ratio_2y: number;
  sortino_ratio_3y: number;
  calmar_ratio_1y: number;
  calmar_ratio_2y: number;
  calmar_ratio_3y: number;
  var_95_1y: number;
  var_99_1y: number;
  cvar_95_1y: number;
  cvar_99_1y: number;
  skewness_1y: number;
  kurtosis_1y: number;
  max_consecutive_loss_days: number;
  beta_1y: number;
  beta_2y: number;
  beta_3y: number;
  tracking_error_1y: number;
  tracking_error_2y: number;
  tracking_error_3y: number;
  upside_capture_1y: number;
  downside_capture_1y: number;
  r_squared_1y: number;
}

export interface StyleAnalysis {
  concentration_level: string;
  top_10_concentration: number;
  top_5_concentration: number;
  hhi_index: number;
  major_industries: string[];
  industry_allocation_style: string;
  style_consistency_score: number;
  style_drift_detected: boolean;
  market_timing_ability: number;
  treynor_mazuy_stat: number;
}

export interface FundAnalysisResult {
  fund_code: string;
  analysis_date: string;
  period: AnalysisPeriod;
  overall_score: number;
  return_analysis: ReturnAnalysis;
  risk_analysis: RiskAnalysis;
  style_analysis: StyleAnalysis;
}

// API request/response types
export interface FundSearchRequest {
  query?: string;
  fund_type?: FundType;
  company_name?: string;
  limit?: number;
  offset?: number;
}

export interface FundAnalysisRequest {
  fund_code: string;
  periods?: AnalysisPeriod[];
  force_refresh?: boolean;
}

export interface FundComparisonRequest {
  fund_codes: string[];
  period: AnalysisPeriod;
}

export interface FundListResponse {
  funds: Fund[];
  total: number;
  offset: number;
  limit: number;
}

// API response wrapper
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// Chart data types
export interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface PerformanceChartData {
  fund_data: ChartDataPoint[];
  benchmark_data?: ChartDataPoint[];
  fund_name: string;
  benchmark_name?: string;
}

// Dashboard summary types
export interface FundSummary {
  fund: Fund;
  latest_nav: FundNav;
  manager: FundManager;
  recent_analysis?: FundAnalysisResult;
}
