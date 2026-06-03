import React from 'react';
import { AlertTriangle, AlertCircle } from 'lucide-react';

export default function AnomalyPanel({ anomalies }: { anomalies: any[] }) {
  if (!anomalies || anomalies.length === 0) {
    return (
      <div className="text-center py-10 text-gray-400">
        <div className="inline-block p-4 bg-slate-700/30 rounded-full mb-3">
          <AlertCircle className="w-8 h-8 text-green-500 opacity-50" />
        </div>
        <p>No active anomalies detected.</p>
        <p className="text-sm">Store operations are normal.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 h-72 overflow-y-auto pr-2 custom-scrollbar">
      {anomalies.map((anomaly, idx) => (
        <div key={idx} className={`p-4 rounded-lg border-l-4 ${anomaly.severity === 'CRITICAL' ? 'border-red-500 bg-red-500/10' : anomaly.severity === 'HIGH' ? 'border-orange-500 bg-orange-500/10' : 'border-yellow-500 bg-yellow-500/10'}`}>
          <div className="flex items-start gap-3">
            <AlertTriangle className={`w-5 h-5 flex-shrink-0 mt-0.5 ${anomaly.severity === 'CRITICAL' ? 'text-red-500' : 'text-orange-500'}`} />
            <div>
              <p className="font-semibold text-sm">{anomaly.type.replace('_', ' ')}</p>
              <p className="text-xs text-gray-300 mt-1">{anomaly.description}</p>
              <p className="text-xs text-gray-500 mt-2">
                {new Date(anomaly.time).toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
