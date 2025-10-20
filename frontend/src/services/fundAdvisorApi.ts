/**
 * Fund Advisor API Service
 * Handles all API calls to the fund advisor backend endpoints
 */

import { API_BASE_URL } from '../config/api';
import {
  Fund,
  FundAnalysisResult,
  FundAnalysisRequest,
  FundComparisonRequest,
  FundListResponse,
  FundSearchRequest,
  FundManager,
  FundNav,
  ApiResponse,
  AnalysisPeriod
} from '../types/fundAdvisor';

const FUNDADVISOR_BASE_URL = `${API_BASE_URL}/api/v1/fundadvisor`;

class FundAdvisorApiService {
  
  // Generic API call method
  private async apiCall<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${FUNDADVISOR_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error(`API Error for ${endpoint}:`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  // Initialize sample data
  async initializeSampleData(): Promise<ApiResponse<{ message: string }>> {
    return this.apiCall('/initialize-data', { method: 'POST' });
  }

  // Get fund basic information
  async getFundInfo(fundCode: string): Promise<ApiResponse<{
    fund: Fund;
    manager: FundManager;
    latest_nav: FundNav;
  }>> {
    return this.apiCall(`/funds/${fundCode}/info`);
  }

  // Search funds
  async searchFunds(request: FundSearchRequest): Promise<ApiResponse<FundListResponse>> {
    const params = new URLSearchParams();
    
    if (request.query) params.append('query', request.query);
    if (request.fund_type) params.append('fund_type', request.fund_type);
    if (request.company_name) params.append('company_name', request.company_name);
    if (request.limit) params.append('limit', request.limit.toString());
    if (request.offset) params.append('offset', request.offset.toString());

    const queryString = params.toString();
    const endpoint = `/funds/search${queryString ? `?${queryString}` : ''}`;
    
    return this.apiCall(endpoint);
  }

  // Single fund analysis
  async analyzeFund(request: FundAnalysisRequest): Promise<ApiResponse<{
    fund_code: string;
    results: { [key: string]: FundAnalysisResult };
  }>> {
    return this.apiCall('/analysis/single', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Batch fund analysis
  async batchAnalyzeFunds(request: {
    fund_codes: string[];
    periods?: AnalysisPeriod[];
    force_refresh?: boolean;
  }): Promise<ApiResponse<{
    results: { [key: string]: { [key: string]: FundAnalysisResult } };
  }>> {
    return this.apiCall('/analysis/batch', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Compare funds
  async compareFunds(request: FundComparisonRequest): Promise<ApiResponse<{
    comparison_results: {
      [key: string]: FundAnalysisResult;
    };
    summary: {
      best_return: { fund_code: string; return_value: number };
      lowest_risk: { fund_code: string; risk_value: number };
      best_sharpe: { fund_code: string; sharpe_value: number };
    };
  }>> {
    return this.apiCall('/analysis/compare', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Get cached analysis results
  async getCachedResults(
    fundCode: string,
    period?: AnalysisPeriod
  ): Promise<ApiResponse<{ [key: string]: FundAnalysisResult }>> {
    const params = new URLSearchParams();
    if (period) params.append('period', period);
    
    const queryString = params.toString();
    const endpoint = `/analysis/${fundCode}/cached-results${queryString ? `?${queryString}` : ''}`;
    
    return this.apiCall(endpoint);
  }

  // Task management endpoints
  async triggerAnalysis(): Promise<ApiResponse<{ message: string; task_id: string }>> {
    return this.apiCall('/tasks/trigger-analysis', { method: 'POST' });
  }

  async getSchedulerStatus(): Promise<ApiResponse<{
    is_running: boolean;
    last_run: string | null;
    next_run: string | null;
    total_runs: number;
  }>> {
    return this.apiCall('/scheduler/status');
  }

  async triggerDataUpdate(): Promise<ApiResponse<{ message: string; updated_funds: number }>> {
    return this.apiCall('/tasks/trigger-data-update', { method: 'POST' });
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{
    status: string;
    timestamp: string;
    database: string;
    scheduler: string;
  }>> {
    return this.apiCall('/health');
  }
}

export const fundAdvisorApi = new FundAdvisorApiService();
export default fundAdvisorApi;
