import React from 'react';

export default function ActiveZones({ funnel }: { funnel: any }) {
  // Derive simple active zone ranking from funnel data
  const zones = [
    { name: "Entrance Flow", count: funnel.entry_count || 0, max: Math.max(funnel.entry_count || 1, 100) },
    { name: "Aisle Browsing", count: funnel.zone_count || 0, max: Math.max(funnel.entry_count || 1, 100) },
    { name: "Billing Queue", count: funnel.queue_join_count || 0, max: Math.max(funnel.entry_count || 1, 100) },
  ];

  return (
    <div className="space-y-6 mt-4">
      {zones.map((zone, idx) => (
        <div key={idx}>
          <div className="flex justify-between text-sm font-medium mb-2">
            <span className="text-gray-200">{zone.name}</span>
            <span className="text-gray-400">{zone.count} visitors</span>
          </div>
          <div className="h-2 w-full bg-black rounded-full overflow-hidden">
            <div 
              className="h-full bg-[#32D74B] rounded-full transition-all duration-1000 ease-out" 
              style={{ width: `${Math.min((zone.count / zone.max) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  );
}
