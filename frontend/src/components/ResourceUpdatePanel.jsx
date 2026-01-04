import React, { useState } from 'react';
import { Save, Loader2, CheckCircle } from 'lucide-react';

export default function ResourceUpdatePanel({ currentStats, onUpdate }) {
    const [stats, setStats] = useState({
        daily_patients: currentStats.daily_patients || 0,
        staff_on_duty: currentStats.staff_on_duty || 0,
        oxygen_status: currentStats.oxygen_status || 'Normal',
        medicine_status: currentStats.medicine_status || 'Normal'
    });
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setSuccess(false);
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://127.0.0.1:8001/api/v1/auth/status/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(stats)
            });

            if (!response.ok) throw new Error('Failed to update status');
            
            const updatedData = await response.json();
            onUpdate(updatedData); // Callback to refresh parent dashboard
            setSuccess(true);
            setTimeout(() => setSuccess(false), 3000);
        } catch (error) {
            console.error("Update failed:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                <span className="w-2 h-6 bg-blue-600 rounded-full"></span>
                Update Resource Status
            </h3>
            
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
                <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Daily Patients</label>
                    <input 
                        type="number" 
                        value={stats.daily_patients}
                        onChange={(e) => setStats({...stats, daily_patients: parseInt(e.target.value)})}
                        className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-100 outline-none"
                    />
                </div>
                
                <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Staff on Duty</label>
                    <input 
                        type="number" 
                        value={stats.staff_on_duty}
                        onChange={(e) => setStats({...stats, staff_on_duty: parseInt(e.target.value)})}
                        className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-100 outline-none"
                    />
                </div>
                
                <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Oxygen Status</label>
                    <select 
                        value={stats.oxygen_status}
                        onChange={(e) => setStats({...stats, oxygen_status: e.target.value})}
                        className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-100 outline-none bg-white"
                    >
                        <option value="Normal">Normal</option>
                        <option value="Low">Low</option>
                        <option value="Critical">Critical</option>
                    </select>
                </div>
                
                <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Medicine Status</label>
                    <select 
                        value={stats.medicine_status}
                        onChange={(e) => setStats({...stats, medicine_status: e.target.value})}
                        className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-100 outline-none bg-white"
                    >
                        <option value="Normal">Normal</option>
                        <option value="Low">Low</option>
                        <option value="Critical">Critical</option>
                    </select>
                </div>
                
                <button 
                    type="submit" 
                    disabled={loading}
                    className={`px-4 py-2 rounded-lg font-medium text-white transition-all flex items-center justify-center gap-2 ${
                        success ? 'bg-green-600' : 'bg-slate-900 hover:bg-slate-800'
                    }`}
                >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : success ? <CheckCircle className="w-4 h-4" /> : <Save className="w-4 h-4" />}
                    {success ? 'Saved' : 'Update'}
                </button>
            </form>
        </div>
    );
}
