// Main Dashboard Page
import React, { useEffect, useState } from 'react';
import { Activity, Users, Bed, BrainCircuit, RefreshCw, TrendingUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import RiskAlert from '../../components/RiskAlert';
import WorkloadGauge from '../../components/WorkloadGauge';
import ResourceUpdatePanel from '../../components/ResourceUpdatePanel';
import ProtectedRoute from '../../components/ProtectedRoute';
import { useAuth } from '../../context/AuthContext';
import { useRouter } from 'next/router';

export default function Dashboard() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { user, logout } = useAuth(); // Get user to check role
    const router = useRouter();

    const fetchData = async () => {
        // setLoading(true); // Don't set loading on refresh to avoid flicker
        setError(null);
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://127.0.0.1:8001/api/v1/dashboard', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (!response.ok) {
                if (response.status === 401) {
                    logout();
                    return;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            setData(result.data);
        } catch (error) {
            console.error("Fetch error:", error);
            setError("Failed to connect to the Hospital Intelligence System. Please ensure the backend is running.");
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

    if (error) return (
        <div className="flex flex-col h-screen items-center justify-center bg-slate-50 text-slate-800">
            <div className="bg-white p-8 rounded-xl shadow-lg border border-red-100 text-center max-w-md">
                <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Activity className="text-red-500 w-8 h-8" />
                </div>
                <h2 className="text-xl font-bold mb-2">Connection Error</h2>
                <p className="text-slate-500 mb-6">{error}</p>
                <button 
                    onClick={() => { setLoading(true); fetchData(); }}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 mx-auto"
                >
                    <RefreshCw className="w-4 h-4" /> Retry Connection
                </button>
            </div>
        </div>
    );

    // Helper for status badges
    const StatusBadge = ({ status }) => {
        const colors = {
            'normal': 'bg-green-100 text-green-700 border-green-200',
            'low': 'bg-amber-100 text-amber-700 border-amber-200',
            'critical': 'bg-red-100 text-red-700 border-red-200'
        };
        const colorClass = colors[status?.toLowerCase()] || colors['normal'];
        
        return (
            <span className={`px-2 py-1 rounded-md text-xs font-bold border ${colorClass} uppercase tracking-wider`}>
                {status}
            </span>
        );
    };

    return (
        <ProtectedRoute allowedRoles={['hospital', 'admin']}>
            <div className="min-h-screen bg-slate-50">
                {/* Navigation Bar */}
                <nav className="bg-white border-b px-8 py-4 flex justify-between items-center sticky top-0 z-10">
                    <div className="flex items-center gap-2 cursor-pointer" onClick={() => router.push('/')}>
                        <div className="bg-blue-600 p-2 rounded-lg"><BrainCircuit className="text-white" /></div>
                        <h1 className="text-xl font-bold text-slate-800 tracking-tight">AxiomForage <span className="text-blue-600">HealthAI</span></h1>
                    </div>
                    <div className="flex gap-4">
                        <button onClick={fetchData} className="flex items-center gap-2 text-sm bg-slate-100 hover:bg-slate-200 px-4 py-2 rounded-md transition-all">
                            <RefreshCw className="w-4 h-4" /> Refresh Data
                        </button>
                        <button onClick={logout} className="text-sm text-slate-500 hover:text-slate-800">Sign Out</button>
                    </div>
                </nav>

                <main className="p-8 max-w-[1600px] mx-auto space-y-8">
                    {/* TOP ROW: Global Alert Status (Feature 4) */}
                    <RiskAlert level={data.summary.alert_level} />

                    {/* MANAGER PANEL: Resource Update (Only for Managers) */}
                    {user?.role === 'hospital' && (
                        <ResourceUpdatePanel 
                            currentStats={{
                                daily_patients: data.summary.daily_patients,
                                staff_on_duty: data.summary.staff_on_duty,
                                oxygen_status: data.summary.oxygen_status,
                                medicine_status: data.summary.medicine_status
                            }} 
                            onUpdate={(updatedHospital) => {
                                // Optimistically update or re-fetch
                                fetchData();
                            }}
                        />
                    )}

                    {/* SECOND ROW: Key Metrics & Chart */}
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">

                        {/* Feature 3: Workload Gauge & Stats */}
                        <div className="lg:col-span-1 space-y-6">
                            <WorkloadGauge value={data.summary.predicted_workload} label="Staff Pressure Index" />

                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                                    <div className="text-xs font-semibold text-slate-500 uppercase mb-1">ICU Occupancy</div>
                                    <div className="text-2xl font-bold text-slate-800">{data.summary.icu_occupied} <span className="text-xs text-slate-400 font-normal">/ {data.summary.icu_total}</span></div>
                                    <div className="w-full bg-slate-100 h-1.5 rounded-full mt-2 overflow-hidden">
                                        <div 
                                            className={`h-full rounded-full ${data.summary.icu_occupied / data.summary.icu_total > 0.8 ? 'bg-red-500' : 'bg-blue-500'}`} 
                                            style={{ width: `${Math.min((data.summary.icu_occupied / data.summary.icu_total) * 100, 100)}%` }}
                                        ></div>
                                    </div>
                                </div>
                                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                                    <div className="text-xs font-semibold text-slate-500 uppercase mb-1">Staff on Duty</div>
                                    <div className="text-2xl font-bold text-slate-800">{data.summary.staff_on_duty}</div>
                                </div>
                            </div>

                            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm font-medium text-slate-600">Oxygen Status</span>
                                    <StatusBadge status={data.summary.oxygen_status} />
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm font-medium text-slate-600">Medicine Status</span>
                                    <StatusBadge status={data.summary.medicine_status} />
                                </div>
                            </div>

                            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                                <div className="flex items-center gap-3 text-slate-500 mb-2">
                                    <Users size={20} /> <span className="text-sm font-semibold">Predicted Arrivals</span>
                                </div>
                                <div className="text-3xl font-bold">{data.summary.predicted_visits} <span className="text-sm font-normal text-slate-400">Patients</span></div>
                            </div>
                        </div>

                        {/* Feature 1 & 2: Forecasting Chart */}
                        <div className="lg:col-span-3 bg-white p-6 rounded-xl border border-slate-200 shadow-sm min-h-[450px]">
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                                    <Activity className="text-blue-600" /> 7-Day Predictive Load Analysis
                                </h3>
                                <button 
                                    onClick={() => router.push('/hospital/history')}
                                    className="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
                                >
                                    View Full History <TrendingUp className="w-4 h-4" />
                                </button>
                            </div>
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
        </ProtectedRoute>
    );
}
