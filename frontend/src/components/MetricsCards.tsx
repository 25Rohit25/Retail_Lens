import React from 'react';
import { Users, ShoppingCart, Clock, UserCheck } from 'lucide-react';

export default function MetricsCards({ metrics }: { metrics: any }) {
  const formatDwellTime = (seconds: number) => {
    if (!seconds) return '0s';
    if (seconds >= 60) {
      const m = Math.floor(seconds / 60);
      const s = Math.floor(seconds % 60);
      return `${m}m ${s}s`;
    }
    return `${Number(seconds).toFixed(1)}s`;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card title="Live Occupancy" value={metrics?.current_occupancy || 0} icon={<Users className="w-6 h-6 text-accent"/>} />
      <Card title="Staff Active" value={metrics?.staff_count || 0} icon={<UserCheck className="w-6 h-6 text-purple-400"/>} />
      <Card title="Avg Dwell Time" value={formatDwellTime(metrics?.avg_dwell_time_seconds)} icon={<Clock className="w-6 h-6 text-yellow-400"/>} />
      <Card title="Conversion Rate" value={`${metrics?.conversion_rate || 0}%`} icon={<ShoppingCart className="w-6 h-6 text-success"/>} />
    </div>
  );
}

function Card({ title, value, icon }: { title: string, value: string | number, icon: React.ReactNode }) {
  return (
    <div className="bg-panel backdrop-blur-2xl p-6 rounded-3xl shadow-2xl flex items-center justify-between transition-transform duration-300 hover:scale-[1.02]">
      <div>
        <p className="text-sm font-medium text-gray-400 tracking-wide">{title}</p>
        <p className="text-4xl font-semibold tracking-tight mt-1">{value}</p>
      </div>
      <div className="p-4 bg-white/5 rounded-2xl">
        {icon}
      </div>
    </div>
  );
}
