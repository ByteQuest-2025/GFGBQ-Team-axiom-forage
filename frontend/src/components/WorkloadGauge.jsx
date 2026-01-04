import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const WorkloadGauge = ({ value, label }) => {
  const data = [
    { name: 'Value', value: value },
    { name: 'Remaining', value: 100 - value },
  ];
  
  // Color based on value
  let color = '#22c55e'; // green
  if (value > 70) color = '#f59e0b'; // amber
  if (value > 90) color = '#ef4444'; // red

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center justify-center h-full">
      <h3 className="text-slate-500 font-semibold mb-4">{label}</h3>
      <div className="h-40 w-full relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              startAngle={180}
              endAngle={0}
              paddingAngle={5}
              dataKey="value"
            >
              <Cell key="value" fill={color} />
              <Cell key="remaining" fill="#f1f5f9" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex items-center justify-center pt-10">
          <span className="text-3xl font-bold text-slate-800">{value}%</span>
        </div>
      </div>
    </div>
  );
};

export default WorkloadGauge;
