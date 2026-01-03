// Main Dashboard Page
import React, { useEffect, useState } from 'react';
import { Activity, Users, Bed, BrainCircuit, RefreshCw } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import RiskAlert from '../components/RiskAlert';
import WorkloadGauge from '../components/WorkloadGauge';
import RecommendationBox from '../components/RecommendationBox';

export default function Dashboard() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:8001/api/v1/dashboard');
            const result = await response.json();
            setData(result.data);
        } catch (error) {
            console.error("Fetch error:", error);
        }
        setLoading(false);

    };

    useEffect(() => { fetchData(); }, []);

    if (loading) return (
        <div className="flex flex-col h-screen items-center justify-center bg-slate-900 text-white">
            <RefreshCw className="animate-spin w-12 h-12 mb-4 text-blue-400" />
            <p className="text-xl font-medium">Syncing with Hospital Intelligence System...</p>
        </div>
    );

    return (
        <div className="min-h-screen bg-slate-50">
            {/* Navigation Bar */}
            <nav className="bg-white border-b px-8 py-4 flex justify-between items-center sticky top-0 z-10">
                <div className="flex items-center gap-2">
                    <div className="bg-blue-600 p-2 rounded-lg"><BrainCircuit className="text-white" /></div>
                    <h1 className="text-xl font-bold text-slate-800 tracking-tight">AxiomForage <span className="text-blue-600">HealthAI</span></h1>
                </div>
                <button onClick={fetchData} className="flex items-center gap-2 text-sm bg-slate-100 hover:bg-slate-200 px-4 py-2 rounded-md transition-all">
                    <RefreshCw className="w-4 h-4" /> Refresh Data
                </button>
            </nav>

            <main className="p-8 max-w-[1600px] mx-auto space-y-8">
                {/* TOP ROW: Global Alert Status (Feature 4) */}
                <RiskAlert level={data.summary.alert_level} />

                {/* SECOND ROW: Key Metrics & Chart */}
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">

                    {/* Feature 3: Workload Gauge */}
                    <div className="lg:col-span-1 space-y-6">
                        <WorkloadGauge value={data.summary.predicted_workload} label="Staff Pressure Index" />

                        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                            <div className="flex items-center gap-3 text-slate-500 mb-2">
                                <Users size={20} /> <span className="text-sm font-semibold">Predicted Arrivals</span>
                            </div>
                            <div className="text-3xl font-bold">{data.summary.predicted_visits} <span className="text-sm font-normal text-slate-400">Patients</span></div>
                        </div>

                        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                            <div className="flex items-center gap-3 text-slate-500 mb-2">
                                <Bed size={20} /> <span className="text-sm font-semibold">ICU Bed Demand</span>
                            </div>
                            <div className="text-3xl font-bold">{data.forecast[0].icu_demand} <span className="text-sm font-normal text-slate-400">Beds</span></div>
                        </div>
                    </div>

                    {/* Feature 1 & 2: Forecasting Chart */}
                    <div className="lg:col-span-3 bg-white p-6 rounded-xl border border-slate-200 shadow-sm min-h-[450px]">
                        <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                            <Activity className="text-blue-600" /> 7-Day Predictive Load Analysis
                        </h3>
                        <ResponsiveContainer width="100%" height="90%">
                            <LineChart data={data.forecast}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="day_name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                                />
                                <Legend iconType="circle" verticalAlign="top" align="right" height={36} />
                                <Line name="ER Admissions" type="monotone" dataKey="emergency_visits" stroke="#2563eb" strokeWidth={4} dot={{ r: 6, fill: '#2563eb' }} activeDot={{ r: 8 }} />
                                <Line name="ICU Demand" type="monotone" dataKey="icu_demand" stroke="#ef4444" strokeWidth={4} dot={{ r: 6, fill: '#ef4444' }} activeDot={{ r: 8 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* THIRD ROW: Feature 5: Actionable Recommendations */}
                <RecommendationBox recommendations={data.recommendations} alertLevel={data.summary.alert_level} />
            </main>
        </div>
    );
}

// hi i doesnt change 