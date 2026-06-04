import React, { useEffect, useState } from 'react';
import { fetchMetrics, fetchFunnel, fetchAnomalies } from './api';
import MetricsCards from "./components/MetricsCards";
import FunnelChartComponent from "./components/FunnelChartComponent";
import AnomalyPanel from "./components/AnomalyPanel";
import OccupancyTrend from "./components/OccupancyTrend";
import ActiveZones from "./components/ActiveZones";

function App() {
  const [metrics, setMetrics] = useState<any>({});
  const [funnel, setFunnel] = useState<any>({});
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [occupancyHistory, setOccupancyHistory] = useState<any[]>([]);
  const storeId = "store_001";

  useEffect(() => {
    // Poll every 5 seconds for live dashboard feel
    const loadData = async () => {
      try {
        const metricsData = await fetchMetrics(storeId);
        setMetrics(metricsData);
        const nowStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        setOccupancyHistory(prev => {
          const updated = [...prev, { time: nowStr, occupancy: metricsData.current_occupancy || 0 }];
          return updated.slice(-20); // keep last 20 ticks
        });
      } catch (err) { console.error("Metrics error:", err); }

      try {
        const funnelData = await fetchFunnel(storeId);
        setFunnel(funnelData);
      } catch (err) { console.error("Funnel error:", err); }

      try {
        const anomalyData = await fetchAnomalies(storeId);
        setAnomalies(anomalyData.anomalies || []);
      } catch (err) { console.error("Anomalies error:", err); }
    };
    
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen p-6 md:p-12 max-w-[1600px] mx-auto selection:bg-[#0A84FF] selection:text-white">
      <header className="mb-10 pb-6 border-b border-white/10 flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">Store Intelligence</h1>
          <p className="text-gray-400 font-medium tracking-wide mt-2">Live monitoring for {storeId}</p>
        </div>
        <div className="flex items-center gap-3 px-4 py-2 bg-[#1C1C1E] rounded-full shadow-lg border border-white/5">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#32D74B] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-[#32D74B]"></span>
          </span>
          <span className="text-sm text-gray-300 font-semibold tracking-wider">LIVE</span>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-8">
        {/* Top KPI Cards */}
        <div className="lg:col-span-3 xl:col-span-4">
          <MetricsCards metrics={metrics} />
        </div>
        
        {/* Occupancy Trend */}
        <div className="lg:col-span-2 xl:col-span-2 bg-[#1C1C1E]/80 backdrop-blur-2xl p-8 rounded-3xl shadow-2xl border border-white/5">
          <h2 className="text-2xl font-semibold mb-2 text-white tracking-tight">Occupancy Trend</h2>
          <p className="text-sm text-gray-400 mb-4 tracking-wide">Real-time visitor flow</p>
          <OccupancyTrend data={occupancyHistory} />
        </div>

        {/* Funnel Chart */}
        <div className="lg:col-span-1 xl:col-span-1 bg-[#1C1C1E]/80 backdrop-blur-2xl p-8 rounded-3xl shadow-2xl border border-white/5">
          <h2 className="text-2xl font-semibold mb-2 text-white tracking-tight">Conversion</h2>
          <p className="text-sm text-gray-400 mb-4 tracking-wide">Shopper funnel drop-offs</p>
          <FunnelChartComponent data={funnel} />
        </div>

        {/* Anomalies List */}
        <div className="lg:col-span-1 xl:col-span-1 bg-[#1C1C1E]/80 backdrop-blur-2xl p-8 rounded-3xl shadow-2xl border border-white/5 flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-2xl font-semibold text-white tracking-tight">Anomalies</h2>
              <p className="text-sm text-[#FF453A] font-medium tracking-wide mt-1">AI Detection Engine</p>
            </div>
            <span className="px-3 py-1 bg-[#FF453A]/20 text-[#FF453A] rounded-full text-sm font-bold">{anomalies.length}</span>
          </div>
          <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
            <AnomalyPanel anomalies={anomalies} />
          </div>
        </div>
        
        {/* Active Zones Layer */}
        <div className="lg:col-span-3 xl:col-span-4 bg-[#1C1C1E]/80 backdrop-blur-2xl p-8 rounded-3xl shadow-2xl border border-white/5">
            <h2 className="text-2xl font-semibold mb-2 text-white tracking-tight">Active Zones</h2>
            <p className="text-sm text-gray-400 tracking-wide mb-6">Heatmap abstraction by zone</p>
            <ActiveZones funnel={funnel} />
        </div>
      </main>
    </div>
  );
}

export default App;
