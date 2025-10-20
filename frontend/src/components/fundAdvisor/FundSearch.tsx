/**
 * Fund Search Component
 * Allows users to search for funds and view basic information
 */

import React, { useState, useEffect } from 'react';
import { Search, Loader2, Calendar, Building2 } from 'lucide-react';
import { Button } from '../ui/button';
import fundAdvisorApi from '../../services/fundAdvisorApi';
import {
  Fund,
  FundSearchRequest,
  FundType,
  FundStatus,
  FundSummary
} from '../../types/fundAdvisor';

interface FundSearchProps {
  onFundSelect?: (fund: Fund) => void;
  onAnalysisRequest?: (fundCode: string) => void;
}

const FundSearch: React.FC<FundSearchProps> = ({ onFundSelect, onAnalysisRequest }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<FundType | ''>('');
  const [funds, setFunds] = useState<Fund[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [expandedFund, setExpandedFund] = useState<string | null>(null);
  const [fundDetails, setFundDetails] = useState<{ [key: string]: FundSummary }>({});

  const pageSize = 10;

  // Fund type options for dropdown
  const fundTypeOptions = [
    { value: '', label: '全部类型' },
    { value: FundType.STOCK, label: '股票型' },
    { value: FundType.MIXED, label: '混合型' },
    { value: FundType.BOND, label: '债券型' },
    { value: FundType.INDEX, label: '指数型' },
    { value: FundType.MONEY_MARKET, label: '货币市场型' },
    { value: FundType.QDII, label: 'QDII' },
  ];

  // Perform search
  const handleSearch = async (page: number = 0) => {
    setLoading(true);
    setError(null);

    try {
      const request: FundSearchRequest = {
        query: searchQuery.trim() || undefined,
        fund_type: selectedType || undefined,
        limit: pageSize,
        offset: page * pageSize,
      };

      const response = await fundAdvisorApi.searchFunds(request);

      if (response.success && response.data) {
        setFunds(response.data.funds);
        setTotal(response.data.total);
        setCurrentPage(page);
      } else {
        setError(response.error || '搜索失败');
      }
    } catch (err) {
      setError('网络错误，请重试');
    } finally {
      setLoading(false);
    }
  };

  // Load fund details
  const handleFundExpand = async (fundCode: string) => {
    if (expandedFund === fundCode) {
      setExpandedFund(null);
      return;
    }

    setExpandedFund(fundCode);

    // Skip if already loaded
    if (fundDetails[fundCode]) return;

    try {
      const response = await fundAdvisorApi.getFundInfo(fundCode);
      if (response.success && response.data) {
        setFundDetails(prev => ({
          ...prev,
          [fundCode]: {
            fund: response.data!.fund,
            latest_nav: response.data!.latest_nav,
            manager: response.data!.manager,
          }
        }));
      }
    } catch (err) {
      console.error('Failed to load fund details:', err);
    }
  };

  // Format currency
  const formatCurrency = (amount: number): string => {
    if (amount >= 1e8) {
      return `${(amount / 1e8).toFixed(2)}亿`;
    } else if (amount >= 1e4) {
      return `${(amount / 1e4).toFixed(2)}万`;
    }
    return amount.toString();
  };

  // Format fund type
  const formatFundType = (type: FundType): string => {
    const typeMap = {
      [FundType.STOCK]: '股票型',
      [FundType.MIXED]: '混合型',
      [FundType.BOND]: '债券型',
      [FundType.INDEX]: '指数型',
      [FundType.MONEY_MARKET]: '货币市场型',
      [FundType.QDII]: 'QDII',
    };
    return typeMap[type] || type;
  };

  // Format fund status
  const formatFundStatus = (status: FundStatus): { text: string; color: string } => {
    const statusMap = {
      [FundStatus.NORMAL]: { text: '正常', color: 'text-green-600' },
      [FundStatus.SUSPENDED]: { text: '暂停', color: 'text-yellow-600' },
      [FundStatus.CLOSED]: { text: '封闭', color: 'text-red-600' },
    };
    return statusMap[status] || { text: status, color: 'text-gray-600' };
  };

  // Initial search on component mount
  useEffect(() => {
    handleSearch(0);
  }, []);

  return (
    <div className="space-y-6">
      {/* Search Controls */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold mb-4">基金搜索</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          {/* Search Input */}
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="请输入基金代码或名称"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch(0)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Fund Type Select */}
          <div>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value as FundType | '')}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {fundTypeOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Search Button */}
          <div>
            <Button
              onClick={() => handleSearch(0)}
              disabled={loading}
              className="w-full"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
              搜索
            </Button>
          </div>
        </div>

        {/* Search Results Summary */}
        {total > 0 && (
          <div className="text-sm text-gray-600 mb-4">
            找到 {total} 只基金，当前显示第 {currentPage * pageSize + 1}-{Math.min((currentPage + 1) * pageSize, total)} 只
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Fund List */}
      <div className="space-y-4">
        {funds.map((fund) => {
          const isExpanded = expandedFund === fund.fund_code;
          const details = fundDetails[fund.fund_code];
          const statusInfo = formatFundStatus(fund.status);

          return (
            <div key={fund.fund_code} className="bg-white rounded-lg shadow-sm border">
              {/* Fund Basic Info */}
              <div
                className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => handleFundExpand(fund.fund_code)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-mono text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded">
                        {fund.fund_code}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded ${statusInfo.color} bg-opacity-10`}>
                        {statusInfo.text}
                      </span>
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {formatFundType(fund.fund_type)}
                      </span>
                    </div>
                    
                    <h3 className="font-medium text-gray-900 mb-1">{fund.fund_name}</h3>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Building2 className="h-3 w-3" />
                        {fund.company_name}
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        成立于 {new Date(fund.inception_date).toLocaleDateString()}
                      </div>
                      <div>
                        规模 {formatCurrency(fund.total_asset)}
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onFundSelect?.(fund);
                      }}
                    >
                      查看详情
                    </Button>
                    <Button
                      variant="default"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onAnalysisRequest?.(fund.fund_code);
                      }}
                    >
                      分析
                    </Button>
                  </div>
                </div>
              </div>

              {/* Expanded Details */}
              {isExpanded && details && (
                <div className="border-t bg-gray-50 p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {/* Latest NAV */}
                    <div className="bg-white rounded p-3">
                      <h4 className="font-medium text-sm text-gray-700 mb-2">最新净值</h4>
                      <div className="space-y-1">
                        <div className="flex justify-between">
                          <span className="text-xs text-gray-600">单位净值:</span>
                          <span className="text-sm font-medium">{details.latest_nav.unit_nav.toFixed(4)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-xs text-gray-600">累计净值:</span>
                          <span className="text-sm">{details.latest_nav.accumulated_nav.toFixed(4)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-xs text-gray-600">净值日期:</span>
                          <span className="text-xs">{new Date(details.latest_nav.nav_date).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>

                    {/* Fund Manager */}
                    <div className="bg-white rounded p-3">
                      <h4 className="font-medium text-sm text-gray-700 mb-2">基金经理</h4>
                      <div className="space-y-1">
                        <div className="text-sm font-medium">{details.manager.manager_name}</div>
                        <div className="text-xs text-gray-600">{details.manager.education}</div>
                        <div className="text-xs text-gray-600">
                          从业 {details.manager.experience_years} 年
                        </div>
                        <div className="text-xs text-gray-600">
                          在管基金 {details.manager.current_funds_count} 只
                        </div>
                      </div>
                    </div>

                    {/* Fund Details */}
                    <div className="bg-white rounded p-3">
                      <h4 className="font-medium text-sm text-gray-700 mb-2">基金信息</h4>
                      <div className="space-y-1">
                        <div className="flex justify-between">
                          <span className="text-xs text-gray-600">管理费:</span>
                          <span className="text-sm">{(fund.management_fee * 100).toFixed(2)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-xs text-gray-600">托管费:</span>
                          <span className="text-sm">{(fund.custodian_fee * 100).toFixed(2)}%</span>
                        </div>
                        <div className="text-xs text-gray-600 mt-2">
                          <div className="truncate">{fund.investment_target}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Pagination */}
      {total > pageSize && (
        <div className="flex justify-center gap-2">
          <Button
            variant="outline"
            disabled={currentPage === 0 || loading}
            onClick={() => handleSearch(currentPage - 1)}
          >
            上一页
          </Button>
          
          <span className="px-4 py-2 text-sm text-gray-600">
            第 {currentPage + 1} 页，共 {Math.ceil(total / pageSize)} 页
          </span>
          
          <Button
            variant="outline"
            disabled={currentPage >= Math.ceil(total / pageSize) - 1 || loading}
            onClick={() => handleSearch(currentPage + 1)}
          >
            下一页
          </Button>
        </div>
      )}

      {/* No Results */}
      {funds.length === 0 && !loading && !error && (
        <div className="text-center py-12 bg-white rounded-lg border">
          <div className="text-gray-500 mb-2">暂无基金数据</div>
          <Button variant="outline" onClick={() => handleSearch(0)}>
            重新搜索
          </Button>
        </div>
      )}
    </div>
  );
};

export default FundSearch;
