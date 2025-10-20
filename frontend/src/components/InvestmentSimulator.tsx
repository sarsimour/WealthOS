import React, { useState, useEffect, useRef } from 'react';
import axios, { AxiosError } from 'axios';
import { useMutation } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import CountUp from 'react-countup';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause, RefreshCw, BarChart, Calendar, DollarSign, Zap, Target } from 'lucide-react';

interface SimulationParams {
  fund_code: string;
  start_date: string;
  end_date: string;
  amount: number;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  price_strategy: 'period_start' | 'period_end' | 'period_low' | 'period_high';
}

interface SimulationSummary {
  total_investment: number;
  final_asset_value: number;
  total_profit: number;
  total_return_rate: number;
  simulation_period_days: number;
  worst_profit_rate: number;
  max_drawdown: number;
}

interface TimeSeriesDataPoint {
  date: string;
  total_investment: number;
  asset_value: number;
  profit: number;
  profit_rate: number;
}

interface SimulationAPIResponse {
  summary: SimulationSummary;
  time_series: TimeSeriesDataPoint[];
}

interface MetricCardProps {
  title: string;
  value: number;
  prefix?: string;
  suffix?: string;
  color: {
    bg: string;
    border: string;
    text: string;
    title: string;
  };
  icon: React.ReactNode;
}

interface AnimationState {
    playing: boolean;
    currentIndex: number;
    speed: number;
}

// API 调用函数
const runSimulationAPI = async (params: SimulationParams): Promise<SimulationAPIResponse> => {
  // 注意：URL 需要替换为您后端 API 的实际地址
  const { data } = await axios.post<SimulationAPIResponse>('/api/v1/fundadvisor/analysis/investment-simulation', params);
  return data;
};

// 数字卡片组件，带动画效果
const MetricCard: React.FC<MetricCardProps> = ({ title, value, prefix = '', suffix = '', color, icon }) => (
  <motion.div 
    className={`p-6 rounded-2xl border ${color.border} bg-gradient-to-br ${color.bg}`}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
  >
    <div className="flex items-center space-x-3 mb-2">
      <div className={`text-2xl ${color.text}`}>{icon}</div>
      <h3 className={`font-semibold ${color.title}`}>{title}</h3>
    </div>
    <div className={`text-4xl font-bold ${color.text}`}>
      <CountUp
        start={0}
        end={value || 0}
        duration={1.5}
        separator=","
        decimals={suffix === '%' ? 2 : 0}
        decimal="."
        prefix={prefix}
        suffix={suffix}
        preserveValue
      />
    </div>
  </motion.div>
);

// 主组件
const InvestmentSimulator: React.FC = () => {
  // --- State Management ---
  const [params, setParams] = useState<SimulationParams>({
    fund_code: '000300', // 沪深300指数作为示例
    start_date: '2018-01-01',
    end_date: '2023-12-31',
    amount: 1000,
    frequency: 'monthly',
    price_strategy: 'period_start',
  });

  const [simulationData, setSimulationData] = useState<SimulationAPIResponse | null>(null);
  const [animationState, setAnimationState] = useState<AnimationState>({
    playing: false,
    currentIndex: 0,
    speed: 50, // 动画速度 (ms)
  });
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // --- API Mutation ---
  const simulationMutation = useMutation<SimulationAPIResponse, AxiosError<{ detail: string }>, SimulationParams>({
    mutationFn: runSimulationAPI,
    onSuccess: (data) => {
      setSimulationData(data);
      startAnimation(data);
    },
    onError: (error) => {
      console.error("Simulation failed:", error);
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    },
  });

  // --- Animation Logic ---
  const startAnimation = (data: SimulationAPIResponse | null) => {
    if (!data) return;
    if (intervalRef.current) clearInterval(intervalRef.current);
    setAnimationState(prev => ({ ...prev, playing: true, currentIndex: 0 }));
    
    intervalRef.current = setInterval(() => {
      setAnimationState(prev => {
        if (prev.currentIndex >= data.time_series.length - 1) {
          if (intervalRef.current) clearInterval(intervalRef.current);
          return { ...prev, playing: false };
        }
        return { ...prev, currentIndex: prev.currentIndex + 1 };
      });
    }, animationState.speed);
  };

  const pauseAnimation = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setAnimationState(prev => ({ ...prev, playing: false }));
  };

  const resetAnimation = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setAnimationState({ playing: false, currentIndex: 0, speed: 50 });
  };
  
  useEffect(() => {
    return () => {
        if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  // --- Event Handlers ---
  const handleParamChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setParams(prev => ({ 
        ...prev, 
        [name]: name === 'amount' ? parseFloat(value) : value 
    } as SimulationParams));
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    resetAnimation();
    setSimulationData(null);
    simulationMutation.mutate(params);
  };
  
  // --- Chart Options ---
  const getChartOptions = () => {
    if (!simulationData) return {};
    
    const animatedData = simulationData.time_series.slice(0, animationState.currentIndex + 1);
    
    return {
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
      legend: { data: ['Total Investment', 'Asset Value'], bottom: 10 },
      grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
      xAxis: { type: 'category', boundaryGap: false, data: animatedData.map(d => d.date) },
      yAxis: { type: 'value', axisLabel: { formatter: '¥{value}' } },
      series: [
        { name: 'Total Investment', type: 'line', smooth: true, showSymbol: false, data: animatedData.map(d => d.total_investment), lineStyle: { color: '#3b82f6' }, areaStyle: { color: 'rgba(59, 130, 246, 0.1)' } },
        { name: 'Asset Value', type: 'line', smooth: true, showSymbol: false, data: animatedData.map(d => d.asset_value), lineStyle: { color: '#10b981' }, areaStyle: { color: 'rgba(16, 185, 129, 0.2)' } }
      ],
      animation: false
    };
  };

  // --- Derived Data for Display ---
  const currentDisplayData = simulationData ? simulationData.time_series[animationState.currentIndex] : null;
  const finalSummary = simulationData ? simulationData.summary : null;

  return (
    <div className="space-y-8">
      {/* 标题和描述 */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h2 className="text-4xl font-bold bg-gradient-to-r from-slate-900 via-cyan-800 to-cyan-700 bg-clip-text text-transparent mb-2">
          Investment Time Machine
        </h2>
        <p className="text-slate-600 text-lg">
          Visualize the power of dollar-cost averaging. See how consistent investment grows over time.
        </p>
      </motion.div>

      {/* 参数输入区 */}
       <motion.div 
        className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-xl border border-slate-200/60"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-6 items-end">
          <div className="space-y-2">
            <label className="font-semibold text-slate-700">Index Code</label>
            <input type="text" name="fund_code" value={params.fund_code} onChange={handleParamChange} className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-cyan-500 transition"/>
          </div>
          <div className="space-y-2">
            <label className="font-semibold text-slate-700">Start Date</label>
            <input type="date" name="start_date" value={params.start_date} onChange={handleParamChange} className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-cyan-500 transition"/>
          </div>
          <div className="space-y-2">
            <label className="font-semibold text-slate-700">End Date</label>
            <input type="date" name="end_date" value={params.end_date} onChange={handleParamChange} className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-cyan-500 transition"/>
          </div>
          <div className="space-y-2">
            <label className="font-semibold text-slate-700">Amount (¥)</label>
            <input type="number" name="amount" value={params.amount} onChange={handleParamChange} className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-cyan-500 transition"/>
          </div>
          <div className="space-y-2">
            <label className="font-semibold text-slate-700">Frequency</label>
            <select name="frequency" value={params.frequency} onChange={handleParamChange} className="w-full p-2 border rounded-lg bg-white focus:ring-2 focus:ring-cyan-500 transition">
              <option value="monthly">Monthly</option>
              <option value="weekly">Weekly</option>
              <option value="quarterly">Quarterly</option>
              <option value="daily">Daily</option>
            </select>
          </div>
          <button type="submit" disabled={simulationMutation.isPending} className="w-full col-span-1 lg:col-span-1 bg-gradient-to-r from-cyan-500 to-cyan-600 text-white font-bold py-2 px-4 rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
            {simulationMutation.isPending ? 'Calculating...' : 'Run Simulation'}
          </button>
        </form>
      </motion.div>

      {/* 结果展示区 */}
      <AnimatePresence>
        {simulationData && currentDisplayData && finalSummary && (
          <motion.div 
            className="space-y-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <MetricCard title="Current Date" value={Date.parse(currentDisplayData.date)} color={{bg: 'from-slate-50 to-slate-100', border: 'border-slate-200', text: 'text-slate-800', title: 'text-slate-600'}} icon={<Calendar />} />
              <MetricCard title="Total Investment" value={currentDisplayData.total_investment} prefix="¥" color={{bg: 'from-blue-50 to-blue-100', border: 'border-blue-200', text: 'text-blue-800', title: 'text-blue-600'}} icon={<DollarSign />} />
              <MetricCard title="Asset Value" value={currentDisplayData.asset_value} prefix="¥" color={{bg: 'from-emerald-50 to-emerald-100', border: 'border-emerald-200', text: 'text-emerald-800', title: 'text-emerald-600'}} icon={<BarChart />} />
              <MetricCard title="Profit Rate" value={currentDisplayData.profit_rate * 100} suffix="%" color={{bg: 'from-orange-50 to-orange-100', border: 'border-orange-200', text: 'text-orange-800', title: 'text-orange-600'}} icon={<Zap />} />
            </div>

            <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-xl border border-slate-200/60">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-2xl font-bold text-slate-800">Growth Journey</h3>
                <div className="flex items-center space-x-2">
                  {animationState.playing ? (
                    <button onClick={pauseAnimation} className="p-2 bg-slate-200 rounded-full hover:bg-slate-300 transition"><Pause size={16}/></button>
                  ) : (
                    <button onClick={() => startAnimation(simulationData)} disabled={animationState.currentIndex >= simulationData.time_series.length -1} className="p-2 bg-slate-200 rounded-full hover:bg-slate-300 transition disabled:opacity-50"><Play size={16}/></button>
                  )}
                  <button onClick={resetAnimation} className="p-2 bg-slate-200 rounded-full hover:bg-slate-300 transition"><RefreshCw size={16}/></button>
                </div>
              </div>
              <ReactECharts option={getChartOptions()} style={{ height: '400px' }} notMerge={true} lazyUpdate={true} />

              <AnimatePresence>
              {!animationState.playing && animationState.currentIndex >= simulationData.time_series.length - 1 && (
                <motion.div 
                  className="mt-8 pt-6 border-t border-slate-200"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center"><Target className="mr-2 text-cyan-500" />Final Results</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div>
                      <p className="text-sm text-slate-500">Total Return</p>
                      <p className="text-2xl font-semibold text-emerald-600">{(finalSummary.total_return_rate * 100).toFixed(2)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-500">Total Profit</p>
                      <p className="text-2xl font-semibold text-emerald-600">¥{finalSummary.total_profit.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-500">Max Drawdown</p>
                      <p className="text-2xl font-semibold text-red-600">{(finalSummary.max_drawdown * 100).toFixed(2)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-500">Period (Days)</p>
                      <p className="text-2xl font-semibold text-slate-600">{finalSummary.simulation_period_days}</p>
                    </div>
                  </div>
                </motion.div>
              )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default InvestmentSimulator;