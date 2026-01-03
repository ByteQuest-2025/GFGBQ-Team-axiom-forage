// Risk Indicator Component
import React from 'react';
import { AlertOctagon, AlertTriangle, Info, CheckCircle } from 'lucide-react';

const RiskAlert = ({ level }) => {
  const configs = {
    Critical: { color: 'bg-red-600 text-white', icon: <AlertOctagon />, label: 'CRITICAL SURGE WARNING' },
    High: { color: 'bg-orange-500 text-white', icon: <AlertTriangle />, label: 'HIGH LOAD ALERT' },
    Elevated: { color: 'bg-yellow-400 text-black', icon: <Info />, label: 'ELEVATED RISK' },
    Normal: { color: 'bg-green-500 text-white', icon: <CheckCircle />, label: 'SYSTEM STABLE' },
  };

  const { color, icon, label } = configs[level] || configs.Normal;

  return (
    <div className={`flex items-center gap-4 p-4 rounded-lg shadow-lg animate-pulse ${color}`}>
      <div className="w-10 h-10 flex items-center justify-center bg-white/20 rounded-full">
        {icon}
      </div>
      <div>
        <p className="text-xs font-bold opacity-80">CURRENT RISK LEVEL</p>
        <h2 className="text-xl font-black tracking-tight">{label}</h2>
      </div>
    </div>
  );
};

export default RiskAlert;