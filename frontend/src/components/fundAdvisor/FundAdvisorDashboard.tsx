/**
 * Fund Advisor Dashboard
 * Main page integrating all fund advisor functionalities
 */

import React, { useState, useEffect } from 'react';
import { 
  Search, BarChart3, TrendingUp, Shield, 
  Database, Settings, RefreshCw, AlertCircle,
  CheckCircle2, Activity, Clock
} from 'lucide-react';
import { Button } from '../ui/button';
import FundSearch from './FundSearch';
import FundAnalysisResults from './FundAnalysisResults';
import FundComparison from './FundComparison';
import fundAdvisorApi from '../../services/fundAdvisorApi';
import { Fund } from '../../types/fundAdvisor';

interface FundAdvisorDashboardProps {
  onClose?: () => void;
}

const FundAdvisorDashboard: React.FC<FundAdvisorDashboardProps> = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState<'search' | 'analysis' | 'comparison' | 'system'>('search');
  const [selectedFund, setSelectedFund] = useState<Fund | null>(null);
  const [analysisTargetCode, setAnalysisTargetCode] = useState<string | null>(null);
  const [comparisonFunds, setComparisonFunds] = useState<string[]>([]);
  const [systemStatus, setSystemStatus] = useState<{
    database: string;
    scheduler: string;
    is_running: boolean;
    last_run: string | null;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load system status
  const loadSystemStatus = async () => {
    try {
      const [healthResponse, schedulerResponse] = await Promise.all([
        fundAdvisorApi.healthCheck(),
        fundAdvisorApi.getSchedulerStatus()
      ]);

      if (healthResponse.success && healthResponse.data) {
        setSystemStatus({
          database: healthResponse.data.database,
          scheduler: healthResponse.data.scheduler,
          is_running: schedulerResponse.data?.is_running || false,
          last_run: schedulerResponse.data?.last_run || null,
        });
      }
    } catch (err) {
      console.error('Failed to load system status:', err);
    }
  };

  // Initialize sample data
  const initializeSampleData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fundAdvisorApi.initializeSampleData();
      if (response.success) {
        alert('样本数据初始化成功！');
        loadSystemStatus();
      } else {
        setError(response.error || '初始化失败');
      }
    } catch (err) {
      setError('网络错误，请重试');
    } finally {
      setLoading(false);
    }
  };

  // Trigger manual analysis
  const triggerAnalysis = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fundAdvisorApi.triggerAnalysis();
      if (response.success) {
        alert('分析任务已启动！');
        loadSystemStatus();
      } else {
        setError(response.error || '启动失败');
      }
    } catch (err) {
      setError('网络错误，请重试');
    } finally {
      setLoading(false);
    }
  };

  // Trigger data update
  const triggerDataUpdate = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fundAdvisorApi.triggerDataUpdate();
      if (response.success) {
        alert('数据更新任务已启动！');
        loadSystemStatus();
      } else {
        setError(response.error || '启动失败');
      }
    } catch (err) {
      setError('网络错误，请重试');
    } finally {
      setLoading(false);
    }
  };

  // Handle fund selection from search
  const handleFundSelect = (fund: Fund) => {
    setSelectedFund(fund);
    setActiveTab('analysis');
    setAnalysisTargetCode(fund.fund_code);
  };

  // Handle analysis request from search
  const handleAnalysisRequest = (fundCode: string) => {
    setAnalysisTargetCode(fundCode);
    setActiveTab('analysis');
  };


  // Load system status on mount
  useEffect(() => {
    loadSystemStatus();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">基金投顾</h1>
              <p className="text-sm text-gray-600">专业的基金分析与投资建议</p>
            </div>
            
            <div className="flex items-center gap-4">
              {/* System Status Indicators */}
              <div className="flex items-center gap-2 text-sm">
                <div className="flex items-center gap-1">
                  <div className={`w-2 h-2 rounded-full ${
                    systemStatus?.database === 'connected' ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <span className="text-gray-600">数据库</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className={`w-2 h-2 rounded-full ${
                    systemStatus?.is_running ? 'bg-green-500' : 'bg-yellow-500'
                  }`} />
                  <span className="text-gray-600">调度器</span>
                </div>
              </div>

              {onClose && (
                <Button variant="outline" onClick={onClose}>
                  返回
                </Button>
              )}
            </div>
          </div>

          {/* Tab Navigation */}
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { key: 'search', label: '基金搜索', icon: Search },
              { key: 'analysis', label: '基金分析', icon: TrendingUp },
              { key: 'comparison', label: '基金对比', icon: BarChart3 },
              { key: 'system', label: '系统管理', icon: Settings },
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
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-red-600">{error}</p>
            </div>
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'search' && (
          <FundSearch 
            onFundSelect={handleFundSelect}
            onAnalysisRequest={handleAnalysisRequest}
          />
        )}

        {activeTab === 'analysis' && (
          <div>
            {analysisTargetCode ? (
              <FundAnalysisResults 
                fundCode={analysisTargetCode}
                fundInfo={selectedFund || undefined}
                onClose={() => {
                  setAnalysisTargetCode(null);
                  setSelectedFund(null);
                }}
              />
            ) : (
              <div className="text-center py-12 bg-white rounded-lg border">
                <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">请先从基金搜索页面选择要分析的基金</p>
                <Button onClick={() => setActiveTab('search')}>
                  前往搜索
                </Button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'comparison' && (
          <FundComparison 
            initialFunds={comparisonFunds}
            onClose={() => setComparisonFunds([])}
          />
        )}

        {activeTab === 'system' && (
          <div className="space-y-6">
            {/* System Status */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold mb-4">系统状态</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Database className="h-4 w-4 text-blue-500" />
                    <span className="text-sm font-medium text-gray-700">数据库状态</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {systemStatus?.database === 'connected' ? (
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-red-500" />
                    )}
                    <span className="text-sm">
                      {systemStatus?.database === 'connected' ? '已连接' : '连接异常'}
                    </span>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="h-4 w-4 text-green-500" />
                    <span className="text-sm font-medium text-gray-700">调度器状态</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {systemStatus?.is_running ? (
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                    ) : (
                      <Clock className="h-4 w-4 text-yellow-500" />
                    )}
                    <span className="text-sm">
                      {systemStatus?.is_running ? '运行中' : '已停止'}
                    </span>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="h-4 w-4 text-purple-500" />
                    <span className="text-sm font-medium text-gray-700">上次运行</span>
                  </div>
                  <div className="text-sm">
                    {systemStatus?.last_run ? 
                      new Date(systemStatus.last_run).toLocaleString() : 
                      '暂无记录'
                    }
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Shield className="h-4 w-4 text-orange-500" />
                    <span className="text-sm font-medium text-gray-700">系统健康</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <span className="text-sm">正常</span>
                  </div>
                </div>
              </div>

              <Button variant="outline" onClick={loadSystemStatus}>
                <RefreshCw className="h-4 w-4 mr-2" />
                刷新状态
              </Button>
            </div>

            {/* System Operations */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold mb-4">系统操作</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="border rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">初始化数据</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    生成模拟的基金数据，包括基金信息、净值、持仓等
                  </p>
                  <Button 
                    onClick={initializeSampleData}
                    disabled={loading}
                    className="w-full"
                  >
                    {loading ? '初始化中...' : '初始化样本数据'}
                  </Button>
                </div>

                <div className="border rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">触发分析</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    手动启动基金分析任务，计算各项指标
                  </p>
                  <Button 
                    onClick={triggerAnalysis}
                    disabled={loading}
                    className="w-full"
                  >
                    {loading ? '分析中...' : '启动分析任务'}
                  </Button>
                </div>

                <div className="border rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">更新数据</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    模拟数据更新过程，刷新基金净值数据
                  </p>
                  <Button 
                    onClick={triggerDataUpdate}
                    disabled={loading}
                    className="w-full"
                  >
                    {loading ? '更新中...' : '启动数据更新'}
                  </Button>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold mb-4">快速操作</h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                  <div>
                    <h3 className="font-medium text-blue-900">完整演示流程</h3>
                    <p className="text-sm text-blue-600">依次执行：初始化数据 → 启动分析 → 查看结果</p>
                  </div>
                  <Button 
                    onClick={async () => {
                      if (confirm('这将依次执行初始化和分析任务，可能需要几分钟时间，确定继续吗？')) {
                        await initializeSampleData();
                        setTimeout(() => triggerAnalysis(), 2000);
                      }
                    }}
                    disabled={loading}
                  >
                    运行演示
                  </Button>
                </div>

                <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                  <div>
                    <h3 className="font-medium text-green-900">切换到搜索页面</h3>
                    <p className="text-sm text-green-600">开始搜索和分析基金</p>
                  </div>
                  <Button 
                    variant="outline"
                    onClick={() => setActiveTab('search')}
                  >
                    开始使用
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FundAdvisorDashboard;
