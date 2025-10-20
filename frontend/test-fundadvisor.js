/**
 * Fund Advisor Frontend Test Script
 * Tests the integration between frontend and backend APIs
 */

const API_BASE_URL = 'http://localhost:8000/api/v1/fundadvisor';

class FundAdvisorTester {
  async testHealthCheck() {
    console.log('🏥 Testing health check...');
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      console.log('✅ Health check passed:', data);
      return true;
    } catch (error) {
      console.error('❌ Health check failed:', error.message);
      return false;
    }
  }

  async testInitializeSampleData() {
    console.log('🚀 Testing sample data initialization...');
    try {
      const response = await fetch(`${API_BASE_URL}/initialize-data`, {
        method: 'POST',
      });
      const data = await response.json();
      console.log('✅ Sample data initialized:', data);
      return true;
    } catch (error) {
      console.error('❌ Sample data initialization failed:', error.message);
      return false;
    }
  }

  async testFundSearch(query = '招商') {
    console.log(`🔍 Testing fund search with query: "${query}"...`);
    try {
      const params = new URLSearchParams({ query, limit: '5' });
      const response = await fetch(`${API_BASE_URL}/funds/search?${params}`);
      const data = await response.json();
      
      if (data.funds && data.funds.length > 0) {
        console.log(`✅ Found ${data.funds.length} funds:`);
        data.funds.forEach(fund => {
          console.log(`   - ${fund.fund_code}: ${fund.fund_name}`);
        });
        return data.funds[0]; // Return first fund for further testing
      } else {
        console.log('⚠️ No funds found');
        return null;
      }
    } catch (error) {
      console.error('❌ Fund search failed:', error.message);
      return null;
    }
  }

  async testFundInfo(fundCode) {
    console.log(`📊 Testing fund info for: ${fundCode}...`);
    try {
      const response = await fetch(`${API_BASE_URL}/funds/${fundCode}/info`);
      const data = await response.json();
      console.log('✅ Fund info retrieved:', {
        name: data.fund.fund_name,
        type: data.fund.fund_type,
        manager: data.manager.manager_name,
        latestNav: data.latest_nav.unit_nav
      });
      return data;
    } catch (error) {
      console.error('❌ Fund info retrieval failed:', error.message);
      return null;
    }
  }

  async testFundAnalysis(fundCode, periods = ['1y']) {
    console.log(`📈 Testing fund analysis for: ${fundCode}...`);
    try {
      const response = await fetch(`${API_BASE_URL}/analysis/single`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fund_code: fundCode,
          periods: periods,
          force_refresh: true
        })
      });
      const data = await response.json();
      
      if (data.results && Object.keys(data.results).length > 0) {
        console.log('✅ Analysis completed:');
        Object.entries(data.results).forEach(([period, result]) => {
          console.log(`   ${period}: Score ${result.overall_score.toFixed(2)}, Return ${(result.return_analysis.total_return_1y * 100).toFixed(2)}%`);
        });
        return data;
      } else {
        console.log('⚠️ No analysis results');
        return null;
      }
    } catch (error) {
      console.error('❌ Fund analysis failed:', error.message);
      return null;
    }
  }

  async testFundComparison(fundCodes, period = '1y') {
    console.log(`🆚 Testing fund comparison for: ${fundCodes.join(', ')}...`);
    try {
      const response = await fetch(`${API_BASE_URL}/analysis/compare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fund_codes: fundCodes,
          period: period
        })
      });
      const data = await response.json();
      
      if (data.comparison_results && data.summary) {
        console.log('✅ Comparison completed:');
        console.log(`   Best Return: ${data.summary.best_return.fund_code} (${(data.summary.best_return.return_value * 100).toFixed(2)}%)`);
        console.log(`   Lowest Risk: ${data.summary.lowest_risk.fund_code} (${(data.summary.lowest_risk.risk_value * 100).toFixed(2)}%)`);
        console.log(`   Best Sharpe: ${data.summary.best_sharpe.fund_code} (${data.summary.best_sharpe.sharpe_value.toFixed(2)})`);
        return data;
      } else {
        console.log('⚠️ No comparison results');
        return null;
      }
    } catch (error) {
      console.error('❌ Fund comparison failed:', error.message);
      return null;
    }
  }

  async testSchedulerStatus() {
    console.log('⏰ Testing scheduler status...');
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/scheduler-status`);
      const data = await response.json();
      console.log('✅ Scheduler status:', {
        running: data.is_running,
        lastRun: data.last_run,
        totalRuns: data.total_runs
      });
      return data;
    } catch (error) {
      console.error('❌ Scheduler status check failed:', error.message);
      return null;
    }
  }

  async runFullTest() {
    console.log('🎯 Starting Fund Advisor Frontend Integration Test\n');
    
    // 1. Health check
    const healthOk = await this.testHealthCheck();
    if (!healthOk) {
      console.log('❌ Backend is not available. Make sure it\'s running on http://localhost:8000');
      return;
    }
    
    console.log('');
    
    // 2. Initialize sample data
    await this.testInitializeSampleData();
    
    console.log('');
    
    // 3. Search for funds
    const firstFund = await this.testFundSearch();
    if (!firstFund) {
      console.log('❌ No funds available for testing');
      return;
    }
    
    console.log('');
    
    // 4. Get fund info
    await this.testFundInfo(firstFund.fund_code);
    
    console.log('');
    
    // 5. Analyze fund
    await this.testFundAnalysis(firstFund.fund_code);
    
    console.log('');
    
    // 6. Search for more funds for comparison
    const moreFunds = await this.testFundSearch('建信');
    if (moreFunds) {
      const fundCodes = [firstFund.fund_code, moreFunds.fund_code];
      await this.testFundComparison(fundCodes);
    }
    
    console.log('');
    
    // 7. Check scheduler status
    await this.testSchedulerStatus();
    
    console.log('\n🎉 Fund Advisor test completed!');
    console.log('\n📋 Next steps:');
    console.log('   1. Open http://localhost:5173 in your browser');
    console.log('   2. Navigate to the "Fund Advisor" tab');
    console.log('   3. Try searching, analyzing, and comparing funds');
    console.log('   4. Use the system management tab to monitor backend status');
  }
}

// Run the test if this script is executed directly
if (typeof window === 'undefined') {
  // Node.js environment
  const tester = new FundAdvisorTester();
  tester.runFullTest().catch(console.error);
} else {
  // Browser environment
  console.log('Fund Advisor Tester loaded. Use: new FundAdvisorTester().runFullTest()');
}
