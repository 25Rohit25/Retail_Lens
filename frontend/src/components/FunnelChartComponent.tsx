import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function FunnelChartComponent({ data }: { data: any }) {
  const chartData = [
    { name: 'Entries', count: data.entry_count || 0, fill: '#3b82f6' },
    { name: 'Engaged', count: data.zone_count || 0, fill: '#8b5cf6' },
    { name: 'Queued', count: data.queue_join_count || 0, fill: '#f59e0b' },
    { name: 'Purchased', count: data.purchase_count || 0, fill: '#22c55e' },
  ];

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <XAxis type="number" hide />
          <YAxis dataKey="name" type="category" stroke="#8E8E93" width={80} axisLine={false} tickLine={false} fontWeight={500} />
          <Tooltip 
            cursor={{fill: 'rgba(255,255,255,0.05)'}}
            contentStyle={{ backgroundColor: 'rgba(28, 28, 30, 0.9)', backdropFilter: 'blur(10px)', border: 'none', borderRadius: '12px', color: '#fff', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }}
            itemStyle={{ color: '#fff', fontWeight: 600 }}
          />
          <Bar dataKey="count" radius={[0, 16, 16, 0]} barSize={24} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
