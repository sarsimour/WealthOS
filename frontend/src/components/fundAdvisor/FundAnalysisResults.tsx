/**
 * Fund Analysis Results Component
 * Displays comprehensive analysis including return, risk, and style analysis
 */

import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, TrendingDown, Shield, PieChart, 
  BarChart3, AlertCircle, CheckCircle2,
  Info, Loader2
} from 'lucide-react';
import { Button } from '../ui/button';
import fundAdvisorApi from '../../services/fundAdvisorApi';
import {
  FundAnalysisResult,
  FundAnalysisRequest,
  AnalysisPeriod,
  Fund
} from '../../types/fundAdvisor';

interface FundAnalysisResultsProps {
  fundCode: string;
  fundInfo?: Fund;
  onClose?: () => void;
}

const FundAnalysisResults: React.FC<FundAnalysisResultsProps> = ({ 
  fundCode, 
  fundInfo, 
  onClose 
}) => {
  const [analysisResults, setAnalysisResults] = useState<{ [key: string]: FundAnalysisResult }>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<AnalysisPeriod>(AnalysisPeriod.ONE_YEAR);
  const [activeTab, setActiveTab] = useState<'return' | 'risk' | 'style'>('return');

  // Analysis periods for display
  const periodOptions = [
    { value: AnalysisPeriod.ONE_MONTH, label: '1个月' },
    { value: AnalysisPeriod.THREE_MONTHS, label: '3个月' },
    { value: AnalysisPeriod.SIX_MONTHS, label: '6个月' },
    { value: AnalysisPeriod.ONE_YEAR, label: '1年' },
    { value: AnalysisPeriod.TWO_YEARS, label: '2年' },
    { value: AnalysisPeriod.THREE_YEARS, label: '3年' },
    { value: AnalysisPeriod.FIVE_YEARS, label: '5年' },
    { value: AnalysisPeriod.SINCE_INCEPTION, label: '成立以来' },
  ];

  // Load analysis results
  const loadAnalysis = async (forceRefresh: boolean = false) => {
    setLoading(true);
    setError(null);

    try {
      // First try to get cached results
      if (!forceRefresh) {
        const cachedResponse = await fundAdvisorApi.getCachedResults(fundCode);
        if (cachedResponse.success && cachedResponse.data && Object.keys(cachedResponse.data).length > 0) {
          setAnalysisResults(cachedResponse.data);
          setLoading(false);
          return;
        }
      }

      // If no cached results or force refresh, perform new analysis
      const request: FundAnalysisRequest = {
        fund_code: fundCode,
        periods: Object.values(AnalysisPeriod),
        force_refresh: forceRefresh,
      };

      const response = await fundAdvisorApi.analyzeFund(request);
      if (response.success && response.data) {
        setAnalysisResults(response.data.results);
      } else {
        setError(response.error || '分析失败');
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

  // Format number with 2 decimal places
  const formatNumber = (value: number): string => {
    return value.toFixed(2);
  };

  // Get color for performance values
  const getPerformanceColor = (value: number): string => {
    if (value > 0) return 'text-green-600';
    if (value < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  // Get current period analysis
  const currentAnalysis = analysisResults[selectedPeriod];

  // Load analysis on component mount
  useEffect(() => {
    loadAnalysis();
  }, [fundCode]);

  // Render return analysis tab
  const renderReturnAnalysis = () => {
    if (!currentAnalysis) return null;

    const { return_analysis } = currentAnalysis;

    const returnMetrics = [
      { label: '总收益率', value: return_analysis.total_return_1y, period: '1年' },
      { label: '年化收益率', value: return_analysis.annualized_return_1y, period: '1年' },
      { label: '超额收益率', value: return_analysis.excess_return_1y, period: '1年' },
    ];

    const rankingMetrics = [
      { label: '同类排名', value: return_analysis.category_rank_1y, total: 100, period: '1年' },
      { label: '同类百分位', value: return_analysis.category_percentile_1y, period: '1年' },
    ];

    return (
      <div className="space-y-6">
        {/* Overall Score */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">综合评分</h3>
              <p className="text-sm text-gray-600">基于多维度分析的综合评价</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-blue-600">
                {formatNumber(currentAnalysis.overall_score)}
              </div>
              <div className="text-sm text-gray-500">满分 100</div>
            </div>
          </div>
        </div>

        {/* Return Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {returnMetrics.map((metric, index) => (
            <div key={index} className="bg-white border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium text-gray-700">{metric.label}</span>
              </div>
              <div className={`text-2xl font-bold ${getPerformanceColor(metric.value)}`}>
                {formatPercentage(metric.value)}
              </div>
              <div className="text-xs text-gray-500 mt-1">{metric.period}</div>
            </div>
          ))}
        </div>

        {/* Stage Returns */}
        <div className="bg-white border rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-4">阶段收益率</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">1个月</div>
              <div className={`font-semibold ${getPerformanceColor(return_analysis.total_return_1m)}`}>
                {formatPercentage(return_analysis.total_return_1m)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">3个月</div>
              <div className={`font-semibold ${getPerformanceColor(return_analysis.total_return_3m)}`}>
                {formatPercentage(return_analysis.total_return_3m)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">6个月</div>
              <div className={`font-semibold ${getPerformanceColor(return_analysis.total_return_6m)}`}>
                {formatPercentage(return_analysis.total_return_6m)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">1年</div>
              <div className={`font-semibold ${getPerformanceColor(return_analysis.total_return_1y)}`}>
                {formatPercentage(return_analysis.total_return_1y)}
              </div>
            </div>
          </div>
        </div>

        {/* Ranking */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {rankingMetrics.map((metric, index) => (
            <div key={index} className="bg-white border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="h-4 w-4 text-blue-500" />
                <span className="text-sm font-medium text-gray-700">{metric.label}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="text-xl font-bold text-gray-900">
                  {metric.label.includes('百分位') ? 
                    formatPercentage(metric.value) : 
                    `${Math.round(metric.value)}/${metric.total || 'N/A'}`
                  }
                </div>
                {metric.value <= 0.25 && (
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                )}
              </div>
              <div className="text-xs text-gray-500 mt-1">{metric.period}</div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Render risk analysis tab
  const renderRiskAnalysis = () => {
    if (!currentAnalysis) return null;

    const { risk_analysis } = currentAnalysis;

    const riskMetrics = [
      { label: '年化波动率', value: risk_analysis.volatility_1y, unit: '%', icon: TrendingDown },
      { label: '最大回撤', value: risk_analysis.max_drawdown_1y, unit: '%', icon: AlertCircle },
      { label: '夏普比率', value: risk_analysis.sharpe_ratio_1y, unit: '', icon: Shield },
      { label: '索提诺比率', value: risk_analysis.sortino_ratio_1y, unit: '', icon: Shield },
    ];

    const advancedMetrics = [
      { label: '贝塔系数', value: risk_analysis.beta_1y },
      { label: '跟踪误差', value: risk_analysis.tracking_error_1y, unit: '%' },
      { label: '上行捕获率', value: risk_analysis.upside_capture_1y, unit: '%' },
      { label: '下行捕获率', value: risk_analysis.downside_capture_1y, unit: '%' },
      { label: 'VaR (95%)', value: risk_analysis.var_95_1y, unit: '%' },
      { label: 'CVaR (95%)', value: risk_analysis.cvar_95_1y, unit: '%' },
    ];

    return (
      <div className="space-y-6">
        {/* Key Risk Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {riskMetrics.map((metric, index) => {
            const IconComponent = metric.icon;
            return (
              <div key={index} className="bg-white border rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <IconComponent className="h-4 w-4 text-orange-500" />
                  <span className="text-sm font-medium text-gray-700">{metric.label}</span>
                </div>
                <div className="text-xl font-bold text-gray-900">
                  {metric.unit === '%' ? formatPercentage(metric.value) : formatNumber(metric.value)}
                </div>
              </div>
            );
          })}
        </div>

        {/* Risk Distribution */}
        <div className="bg-white border rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-4">风险分布指标</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">偏度</div>
              <div className="font-semibold">{formatNumber(risk_analysis.skewness_1y)}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">峰度</div>
              <div className="font-semibold">{formatNumber(risk_analysis.kurtosis_1y)}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">最大连续亏损天数</div>
              <div className="font-semibold">{risk_analysis.max_consecutive_loss_days}天</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">R²</div>
              <div className="font-semibold">{formatNumber(risk_analysis.r_squared_1y)}</div>
            </div>
          </div>
        </div>

        {/* Advanced Risk Metrics */}
        <div className="bg-white border rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-4">高级风险指标</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {advancedMetrics.map((metric, index) => (
              <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-b-0">
                <span className="text-sm text-gray-600">{metric.label}</span>
                <span className="font-medium">
                  {metric.unit === '%' ? formatPercentage(metric.value) : formatNumber(metric.value)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  // Render style analysis tab
  const renderStyleAnalysis = () => {
    if (!currentAnalysis) return null;

    const { style_analysis } = currentAnalysis;

    return (
      <div className="space-y-6">
        {/* Position Concentration */}
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <PieChart className="h-4 w-4 text-purple-500" />
            <h4 className="font-medium text-gray-900">持仓集中度</h4>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">集中度水平</div>
              <div className="font-semibold text-lg">{style_analysis.concentration_level}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">前10大持仓占比</div>
              <div className="font-semibold text-lg">
                {formatPercentage(style_analysis.top_10_concentration)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">HHI指数</div>
              <div className="font-semibold text-lg">{formatNumber(style_analysis.hhi_index)}</div>
            </div>
          </div>
        </div>

        {/* Industry Allocation */}
        <div className="bg-white border rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-4">行业配置</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <div className="text-xs text-gray-500 mb-1">配置风格</div>
              <div className="font-semibold">{style_analysis.industry_allocation_style}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">主要行业</div>
              <div className="text-sm">
                {style_analysis.major_industries.slice(0, 3).join(', ')}
                {style_analysis.major_industries.length > 3 && '...'}
              </div>
            </div>
          </div>

          {/* Major Industries List */}
          <div>
            <div className="text-xs text-gray-500 mb-2">重点配置行业</div>
            <div className="flex flex-wrap gap-2">
              {style_analysis.major_industries.map((industry, index) => (
                <span 
                  key={index} 
                  className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded"
                >
                  {industry}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Style Consistency */}
        <div className="bg-white border rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-4">投资风格</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">风格一致性评分</div>
              <div className="font-semibold text-lg text-blue-600">
                {formatNumber(style_analysis.style_consistency_score)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">风格漂移</div>
              <div className="font-semibold">
                {style_analysis.style_drift_detected ? (
                  <span className="text-red-600">检测到</span>
                ) : (
                  <span className="text-green-600">未检测到</span>
                )}
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">择时能力</div>
              <div className="font-semibold">{formatNumber(style_analysis.market_timing_ability)}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">T-M统计量</div>
              <div className="font-semibold">{formatNumber(style_analysis.treynor_mazuy_stat)}</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">正在分析基金数据...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center gap-2 mb-2">
          <AlertCircle className="h-5 w-5 text-red-500" />
          <h3 className="font-medium text-red-800">分析失败</h3>
        </div>
        <p className="text-red-600 mb-4">{error}</p>
        <Button variant="outline" onClick={() => loadAnalysis(true)}>
          重新分析
        </Button>
      </div>
    );
  }

  if (!currentAnalysis) {
    return (
      <div className="text-center py-12">
        <Info className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 mb-4">暂无该时期的分析数据</p>
        <Button onClick={() => loadAnalysis(true)}>
          开始分析
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {fundInfo ? fundInfo.fund_name : fundCode} 分析报告
            </h2>
            <p className="text-sm text-gray-600">
              分析时间: {new Date(currentAnalysis.analysis_date).toLocaleString()}
            </p>
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => loadAnalysis(true)}>
              刷新分析
            </Button>
            {onClose && (
              <Button variant="outline" onClick={onClose}>
                关闭
              </Button>
            )}
          </div>
        </div>

        {/* Period Selector */}
        <div className="flex flex-wrap gap-2">
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
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="border-b">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {[
              { key: 'return', label: '收益分析', icon: TrendingUp },
              { key: 'risk', label: '风险分析', icon: Shield },
              { key: 'style', label: '风格分析', icon: PieChart },
            ].map(tab => {
              const IconComponent = tab.icon;
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.key
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <IconComponent className="h-4 w-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'return' && renderReturnAnalysis()}
          {activeTab === 'risk' && renderRiskAnalysis()}
          {activeTab === 'style' && renderStyleAnalysis()}
        </div>
      </div>
    </div>
  );
};

export default FundAnalysisResults;