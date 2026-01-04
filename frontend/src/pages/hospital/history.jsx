import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, BarChart, Bar } from 'recharts';
import { BrainCircuit, Calendar, Activity, TrendingUp, AlertTriangle, ArrowLeft } from 'lucide-react';
import ProtectedRoute from '../../components/ProtectedRoute';
import { useAuth } from '../../context/AuthContext';

export default function HistoryPage() {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const router = useRouter();
    const { logout } = useAuth();

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await fetch('http://127.0.0.1:8001/api/v1/predictions/history?limit=30', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    if (response.status === 401) {
                        logout();
                        return;
                    }
                    throw new Error('Failed to fetch history');
                }

                const result = await response.json();
                if (result.success) {
                    // Process data for charts
                    // Reverse to show oldest -> newest left to right
                    const processedData = result.predictions.reverse().map(p => ({
                        ...p,
                        date_short: new Date(p.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                        er_surge_val: (p.er_surge_pct * 100).toFixed(1),
                        icu_surge_val: (p.icu_surge_pct * 100).toFixed(1),
                        risk_score_val: (p.risk_score * 100).toFixed(1)
                    }));
                    setHistory(processedData);
                }
            } catch (err) {
                console.error(err);
                setError("Could not load historical data.");
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, []);

    if (loading) return (
        <div className="flex flex-col h-screen items-center justify-center bg-slate-50 text-slate-800">
            <Activity className="animate-spin w-10 h-10 text-blue-600 mb-4" />
            <p className="font-medium">Loading historical trends...</p>
        </div>
    );

    return (
        <ProtectedRoute allowedRoles={['hospital', 'admin']}>
            <div className="min-h-screen bg-slate-50">
                {/* Navigation */}
                <nav className="bg-white border-b px-8 py-4 flex justify-between items-center sticky top-0 z-10">
                    <div className="flex items-center gap-4">
                        <button onClick={() => router.back()} className="p-2 hover:bg-slate-100 rounded-full transition-colors">
                            <ArrowLeft className="w-5 h-5 text-slate-600" />
                        </button>
                        <div className="flex items-center gap-2">
                            <div className="bg-blue-600 p-2 rounded-lg"><BrainCircuit className="text-white w-5 h-5" /></div>
                            <h1 className="text-xl font-bold text-slate-800 tracking-tight">Historical Analysis</h1>
                        </div>
                    </div>
                </nav>

                <main className="p-8 max-w-[1600px] mx-auto space-y-8">
                    
                    {/* Header Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                            <div className="flex items-center gap-3 text-slate-500 mb-2">
                                <Calendar className="w-5 h-5" />
                                <span className="text-sm font-semibold">Data Points</span>
                            </div>
                            <div className="text-3xl font-bold text-slate-800">{history.length} <span className="text-sm font-normal text-slate-400">Days</span></div>
                        </div>
                        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                            <div className="flex items-center gap-3 text-slate-500 mb-2">
                                <TrendingUp className="w-5 h-5" />
                                <span className="text-sm font-semibold">Avg Risk Score</span>
                            </div>
                            <div className="text-3xl font-bold text-slate-800">
                                {(history.reduce((acc, curr) => acc + curr.risk_score, 0) / history.length * 100).toFixed(1)}%
                            </div>
                        </div>
                        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                            <div className="flex items-center gap-3 text-slate-500 mb-2">
                                <AlertTriangle className="w-5 h-5" />
                                <span className="text-sm font-semibold">High Risk Days</span>
                            </div>
                            <div className="text-3xl font-bold text-slate-800">
                                {history.filter(h => h.risk_level === 'High' || h.risk_level === 'Critical').length}
                            </div>
                        </div>
                    </div>

                    {/* Chart 1: Risk Score Trend */}
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                            <Activity className="text-blue-600 w-5 h-5" /> Risk Score Trend (Last 30 Days)
                        </h3>
                        <div className="h-[400px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={history}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                    <XAxis dataKey="date_short" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} unit="%" />
                                    <Tooltip 
                                        contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                                    />
                                    <Legend />
                                    <Line 
                                        type="monotone" 
                                        dataKey="risk_score_val" 
                                        name="Risk Score" 
                                        stroke="#2563eb" 
                                        strokeWidth={3} 
                                        dot={{ r: 4, fill: '#2563eb' }} 
                                        activeDot={{ r: 6 }} 
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Chart 2: ER & ICU Surge Trends */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                            <h3 className="text-lg font-bold text-slate-800 mb-6">ER Visit Surge Trend</h3>
                            <div className="h-[300px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={history}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                        <XAxis dataKey="date_short" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                                        <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} unit="%" />
                                        <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }} />
                                        <Line type="monotone" dataKey="er_surge_val" name="ER Surge" stroke="#0ea5e9" strokeWidth={2} dot={false} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                            <h3 className="text-lg font-bold text-slate-800 mb-6">ICU Demand Trend</h3>
                            <div className="h-[300px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={history}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                        <XAxis dataKey="date_short" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                                        <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} unit="%" />
                                        <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }} />
                                        <Line type="monotone" dataKey="icu_surge_val" name="ICU Surge" stroke="#ef4444" strokeWidth={2} dot={false} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>

                    {/* Past Risk Levels Table */}
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <div className="p-6 border-b border-slate-100">
                            <h3 className="text-lg font-bold text-slate-800">Historical Risk Log</h3>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-slate-50 text-slate-500 font-medium">
                                    <tr>
                                        <th className="px-6 py-4">Date</th>
                                        <th className="px-6 py-4">Risk Level</th>
                                        <th className="px-6 py-4">Risk Score</th>
                                        <th className="px-6 py-4">ER Surge</th>
                                        <th className="px-6 py-4">ICU Surge</th>
                                        <th className="px-6 py-4">Resources Needed</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {history.slice().reverse().map((day, i) => ( // Show newest first in table
                                        <tr key={i} className="hover:bg-slate-50 transition-colors">
                                            <td className="px-6 py-4 font-medium text-slate-800">{new Date(day.date).toLocaleDateString()}</td>
                                            <td className="px-6 py-4">
                                                <span className={`px-2 py-1 rounded-full text-xs font-bold uppercase tracking-wider
                                                    ${day.risk_level === 'Low' ? 'bg-green-100 text-green-700' : 
                                                      day.risk_level === 'High' ? 'bg-orange-100 text-orange-700' : 
                                                      day.risk_level === 'Critical' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
                                                    {day.risk_level}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-slate-600">{day.risk_score_val}%</td>
                                            <td className="px-6 py-4 text-slate-600">+{day.er_surge_val}%</td>
                                            <td className="px-6 py-4 text-slate-600">+{day.icu_surge_val}%</td>
                                            <td className="px-6 py-4 text-slate-600">
                                                {day.beds_needed > 0 && <span className="mr-2">{day.beds_needed} Beds</span>}
                                                {day.staff_needed > 0 && <span>{day.staff_needed} Staff</span>}
                                                {day.beds_needed === 0 && day.staff_needed === 0 && <span className="text-slate-400">-</span>}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                </main>
            </div>
        </ProtectedRoute>
    );
}
