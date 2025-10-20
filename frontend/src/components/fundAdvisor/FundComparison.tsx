/**
 * Fund Comparison Component
 * Allows users to compare multiple funds side by side
 */

import React, { useState, useEffect } from 'react';
import { 
  Plus, X, BarChart3, Shield, 
  Crown, Target, Loader2, AlertCircle 
} from 'lucide-react';
import { Button } from '../ui/button';
import fundAdvisorApi from '../../services/fundAdvisorApi';
import {
  Fund,
  FundAnalysisResult,
  FundComparisonRequest,
  AnalysisPeriod,
  FundSearchRequest
} from '../../types/fundAdvisor';

interface FundComparisonProps {
  initialFunds?: string[];
  onClose?: () => void;
}

const FundComparison: React.FC<FundComparisonProps> = ({ initialFunds = [], onClose }) => {
  const [selectedFunds, setSelectedFunds] = useState<string[]>(initialFunds);
  const [fundSearchQuery, setFundSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Fund[]>([]);
  const [comparisonResults, setComparisonResults] = useState<{
    [key: string]: FundAnalysisResult;
  }>({});
  const [summary, setSummary] = useState<{
    best_return: { fund_code: string; return_value: number };
    lowest_risk: { fund_code: string; risk_value: number };
    best_sharpe: { fund_code: string; sharpe_value: number };
  } | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<AnalysisPeriod>(AnalysisPeriod.ONE_YEAR);
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSearch, setShowSearch] = useState(false);

  // Period options
  const periodOptions = [
    { value: AnalysisPeriod.ONE_MONTH, label: '1个月' },
    { value: AnalysisPeriod.THREE_MONTHS, label: '3个月' },
    { value: AnalysisPeriod.SIX_MONTHS, label: '6个月' },
    { value: AnalysisPeriod.ONE_YEAR, label: '1年' },
    { value: AnalysisPeriod.TWO_YEARS, label: '2年' },
    { value: AnalysisPeriod.THREE_YEARS, label: '3年' },
  ];

  // Search for funds
  const searchFunds = async () => {
    if (!fundSearchQuery.trim()) return;

    setSearchLoading(true);
    try {
      const request: FundSearchRequest = {
        query: fundSearchQuery.trim(),
        limit: 10,
      };

      const response = await fundAdvisorApi.searchFunds(request);
      if (response.success && response.data) {
        setSearchResults(response.data.funds);
      }
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setSearchLoading(false);
    }
  };

  // Add fund to comparison
  const addFund = (fundCode: string) => {
    if (selectedFunds.length >= 5) {
      alert('最多只能比较5只基金');
      return;
    }
    
    if (!selectedFunds.includes(fundCode)) {
      setSelectedFunds([...selectedFunds, fundCode]);
      setShowSearch(false);
      setFundSearchQuery('');
      setSearchResults([]);
    }
  };

  // Remove fund from comparison
  const removeFund = (fundCode: string) => {
    setSelectedFunds(selectedFunds.filter(code => code !== fundCode));
  };

  // Load comparison data
  const loadComparison = async () => {
    if (selectedFunds.length < 2) return;

    setLoading(true);
    setError(null);

    try {
      const request: FundComparisonRequest = {
        fund_codes: selectedFunds,
        period: selectedPeriod,
      };

      const response = await fundAdvisorApi.compareFunds(request);
      if (response.success && response.data) {
        setComparisonResults(response.data.comparison_results);
        setSummary(response.data.summary);
      } else {
        setError(response.error || '对比分析失败');
      }
    } catch (err) {
      setError('网络错误，请重试');
    } finally {
      setLoading(false);
    }
  };

  // Format percentage
  const formatPercentage = (value: number): string => {
    return `${(value * 100).toFixed(2)}%`;
  };

  // Format number
  const formatNumber = (value: number, decimals: number = 2): string => {
    return value.toFixed(decimals);
  };

  // Get performance color
  const getPerformanceColor = (value: number): string => {
    if (value > 0) return 'text-green-600';
    if (value < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  // Load comparison when funds or period changes
  useEffect(() => {
    if (selectedFunds.length >= 2) {
      loadComparison();
    }
  }, [selectedFunds, selectedPeriod]);

  // Auto-search when query changes
  useEffect(() => {
    const timer = setTimeout(() => {
      if (fundSearchQuery.trim()) {
        searchFunds();
      } else {
        setSearchResults([]);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [fundSearchQuery]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">基金对比分析</h2>
            <p className="text-sm text-gray-600">选择2-5只基金进行对比分析</p>
          </div>
          
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              onClick={() => setShowSearch(!showSearch)}
              disabled={selectedFunds.length >= 5}
            >
              <Plus className="h-4 w-4 mr-2" />
              添加基金
            </Button>
            {onClose && (
              <Button variant="outline" onClick={onClose}>
                关闭
              </Button>
            )}
          </div>
        </div>

        {/* Period Selector */}
        <div className="flex flex-wrap gap-2 mb-4">
          {periodOptions.map(option => (
            <button
              key={option.value}
              onClick={() => setSelectedPeriod(option.value)}
              className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                selectedPeriod === option.value
                  ? 'bg-blue-100 text-blue-700 font-medium'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>

        {/* Selected Funds */}
        <div className="flex flex-wrap gap-2">
          {selectedFunds.map(fundCode => (
            <div 
              key={fundCode} 
              className="flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-lg"
            >
              <span className="font-mono text-sm">{fundCode}</span>
              <button 
                onClick={() => removeFund(fundCode)}
                className="text-blue-500 hover:text-blue-700"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
          
          {selectedFunds.length === 0 && (
            <div className="text-gray-500 text-sm py-2">
              请选择要对比的基金
            </div>
          )}
        </div>
      </div>

      {/* Fund Search Panel */}
      {showSearch && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="font-medium text-gray-900 mb-4">搜索基金</h3>
          
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              placeholder="输入基金代码或名称"
              value={fundSearchQuery}
              onChange={(e) => setFundSearchQuery(e.target.value)}
              className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && searchFunds()}
            />
            <Button onClick={searchFunds} disabled={searchLoading}>
              {searchLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : '搜索'}
            </Button>
          </div>

          {/* Search Results */}
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {searchResults.map(fund => (
              <div 
                key={fund.fund_code}
                className="flex justify-between items-center p-3 border rounded-lg hover:bg-gray-50"
              >
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-sm text-blue-600">{fund.fund_code}</span>
                    <span className="text-xs text-gray-500">{fund.fund_type}</span>
                  </div>
                  <div className="font-medium text-sm text-gray-900">{fund.fund_name}</div>
                  <div className="text-xs text-gray-600">{fund.company_name}</div>
                </div>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => addFund(fund.fund_code)}
                  disabled={selectedFunds.includes(fund.fund_code)}
                >
                  {selectedFunds.includes(fund.fund_code) ? '已添加' : '添加'}
                </Button>
              </div>
            ))}
            
            {fundSearchQuery && searchResults.length === 0 && !searchLoading && (
              <div className="text-center py-4 text-gray-500">
                没有找到相关基金
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <p className="text-red-600">{error}</p>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center p-12">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-blue-500 mx-auto mb-4" />
            <p className="text-gray-600">正在生成对比分析...</p>
          </div>
        </div>
      )}

      {/* Comparison Results */}
      {!loading && selectedFunds.length >= 2 && Object.keys(comparisonResults).length > 0 && (
        <div className="space-y-6">
          {/* Summary Cards */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Crown className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium text-green-800">最佳收益</span>
                </div>
                <div className="font-mono text-sm text-green-700 mb-1">
                  {summary.best_return.fund_code}
                </div>
                <div className="text-lg font-bold text-green-600">
                  {formatPercentage(summary.best_return.return_value)}
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="h-4 w-4 text-blue-600" />
                  <span className="text-sm font-medium text-blue-800">最低风险</span>
                </div>
                <div className="font-mono text-sm text-blue-700 mb-1">
                  {summary.lowest_risk.fund_code}
                </div>
                <div className="text-lg font-bold text-blue-600">
                  {formatPercentage(summary.lowest_risk.risk_value)}
                </div>
              </div>

              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="h-4 w-4 text-purple-600" />
                  <span className="text-sm font-medium text-purple-800">最佳夏普</span>
                </div>
                <div className="font-mono text-sm text-purple-700 mb-1">
                  {summary.best_sharpe.fund_code}
                </div>
                <div className="text-lg font-bold text-purple-600">
                  {formatNumber(summary.best_sharpe.sharpe_value)}
                </div>
              </div>
            </div>
          )}

          {/* Detailed Comparison Table */}
          <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
            <div className="px-6 py-4 border-b">
              <h3 className="font-medium text-gray-900">详细对比</h3>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      指标
                    </th>
                    {selectedFunds.map(fundCode => (
                      <th key={fundCode} className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {fundCode}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {/* Return Metrics */}
                  <tr className="bg-green-50">
                    <td colSpan={selectedFunds.length + 1} className="px-6 py-2 text-xs font-medium text-green-800 uppercase">
                      收益指标
                    </td>
                  </tr>
                  
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">总收益率</td>
                    {selectedFunds.map(fundCode => {
                      const result = comparisonResults[fundCode];
                      const value = result?.return_analysis.total_return_1y || 0;
                      return (
                        <td key={fundCode} className={`px-6 py-4 whitespace-nowrap text-sm font-medium text-center ${getPerformanceColor(value)}`}>
                          {formatPercentage(value)}
                        </td>
                      );
                    })}
                  </tr>

                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">年化收益率</td>
                    {selectedFunds.map(fundCode => {
                      const result = comparisonResults[fundCode];
                      const value = result?.return_analysis.annualized_return_1y || 0;
                      return (
                        <td key={fundCode} className={`px-6 py-4 whitespace-nowrap text-sm font-medium text-center ${getPerformanceColor(value)}`}>
                          {formatPercentage(value)}
                        </td>
                      );
                    })}
                  </tr>

                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">超额收益率</td>
                    {selectedFunds.map(fundCode => {
                      const result = comparisonResults[fundCode];
                      const value = result?.return_analysis.excess_return_1y || 0;
                      return (
                        <td key={fundCode} className={`px-6 py-4 whitespace-nowrap text-sm font-medium text-center ${getPerformanceColor(value)}`}>
                          {formatPercentage(value)}
                        </td>
                      );
                    })}
                  </tr>

                  {/* Risk Metrics */}
                  <tr className="bg-orange-50">
                    <td colSpan={selectedFunds.length + 1} className="px-6 py-2 text-xs font-medium text-orange-800 uppercase">
                      风险指标
                    </td>
                  </tr>

                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">年化波动率</td>
                    {selectedFunds.map(fundCode => {
                      const result = comparisonResults[fundCode];
                      const value = result?.risk_analysis.volatility_1y || 0;
                      return (
                        <td key={fundCode} className="px-6 py-4 whitespace-nowrap text-sm font-medium text-center text-gray-900">
                          {formatPercentage(value)}
                        </td>
                      );
                    })}
                  </tr>

                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">最大回撤</td>
                    {selectedFunds.map(fundCode => {
                      const result = comparisonResults[fundCode];
                      const value = result?.risk_analysis.max_drawdown_1y || 0;
                      return (
                        <td key={fundCode} className="px-6 py-4 whitespace-nowrap text-sm font-medium text-center text-red-600">
                          {formatPercentage(value)}
                        </td>
                      );
                    })}
                  </tr>

                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">夏普比率</td>
                    {selectedFunds.map(fundCode => {
                      const result = comparisonResults[fundCode];
                      const value = result?.risk_analysis.sharpe_ratio_1y || 0;
                      return (
                        <td key={fundCode} className="px-6 py-4 whitespace-nowrap text-sm font-medium text-center text-gray-900">
                          {formatNumber(value)}
                        </td>
                      );
                    })}
                  </tr>

                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">贝塔系数</td>
                    {selectedFunds.map(fundCode => {
                      const result = comparisonResults[fundCode];
                      const value = result?.risk_analysis.beta_1y || 0;
                      return (
                        <td key={fundCode} className="px-6 py-4 whitespace-nowrap text-sm font-medium text-center text-gray-900">
                          {formatNumber(value)}
                        </td>
                      );
                    })}
                  </tr>

                  {/* Style Metrics */}
                  <tr className="bg-purple-50">
                    <td colSpan={selectedFunds.length + 1} className="px-6 py-2 text-xs font-medium text-purple-800 uppercase">
                      风格指标
                    </td>
                  </tr>

                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">持仓集中度</td>
                    {selectedFunds.map(fundCode => {
                      const result = comparisonResults[fundCode];
                      const value = result?.style_analysis.concentration_level || '-';
                      return (
                        <td key={fundCode} className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-900">
                          {value}
                        </td>
                      );
                    })}
                  </tr>

                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">前10大持仓占比</td>
                    {selectedFunds.map(fundCode => {
                      const result = comparisonResults[fundCode];
                      const value = result?.style_analysis.top_10_concentration || 0;
                      return (
                        <td key={fundCode} className="px-6 py-4 whitespace-nowrap text-sm font-medium text-center text-gray-900">
                          {formatPercentage(value)}
                        </td>
                      );
                    })}
                  </tr>

                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">综合评分</td>
                    {selectedFunds.map(fundCode => {
                      const result = comparisonResults[fundCode];
                      const value = result?.overall_score || 0;
                      return (
                        <td key={fundCode} className="px-6 py-4 whitespace-nowrap text-sm font-bold text-center text-blue-600">
                          {formatNumber(value)}
                        </td>
                      );
                    })}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {selectedFunds.length < 2 && !loading && (
        <div className="text-center py-12 bg-white rounded-lg border">
          <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">请选择至少2只基金进行对比分析</p>
          <Button onClick={() => setShowSearch(true)}>
            <Plus className="h-4 w-4 mr-2" />
            添加基金
          </Button>
        </div>
      )}
    </div>
  );
};

export default FundComparison;
