import React from 'react';
import { AreaChart, Area, XAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function OccupancyTrend({ data }: { data: any[] }) {
  return (
    <div className="w-full h-48 mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 0, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorOccupancy" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#0A84FF" stopOpacity={0.4}/>
              <stop offset="95%" stopColor="#0A84FF" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis dataKey="time" hide />
          <Tooltip 
            contentStyle={{ backgroundColor: 'rgba(28, 28, 30, 0.9)', backdropFilter: 'blur(10px)', border: 'none', borderRadius: '12px', color: '#fff', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }}
            itemStyle={{ color: '#0A84FF', fontWeight: 600 }}
            labelStyle={{ color: '#8E8E93', marginBottom: '4px' }}
          />
          <Area type="monotone" dataKey="occupancy" stroke="#0A84FF" strokeWidth={3} fillOpacity={1} fill="url(#colorOccupancy)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
