import React from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import { useAuth } from '../../context/AuthContext';
import { Shield, Users, Activity, LogOut } from 'lucide-react';

export default function AdminDashboard() {
    const { logout } = useAuth();

    return (
        <ProtectedRoute allowedRoles={['admin']}>
            <div className="min-h-screen bg-slate-50">
                <nav className="bg-slate-900 text-white px-8 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <Shield className="text-purple-400" />
                        <h1 className="text-xl font-bold">Admin Console</h1>
                    </div>
                    <button onClick={logout} className="flex items-center gap-2 text-sm hover:text-purple-300 transition-colors">
                        <LogOut className="w-4 h-4" /> Sign Out
                    </button>
                </nav>

                <main className="p-8 max-w-6xl mx-auto">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="p-2 bg-purple-100 rounded-lg">
                                    <Users className="w-6 h-6 text-purple-600" />
                                </div>
                                <h3 className="font-semibold text-slate-700">Total Hospitals</h3>
                            </div>
                            <p className="text-3xl font-bold text-slate-900">12</p>
                        </div>
                        
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="p-2 bg-blue-100 rounded-lg">
                                    <Activity className="w-6 h-6 text-blue-600" />
                                </div>
                                <h3 className="font-semibold text-slate-700">System Status</h3>
                            </div>
                            <p className="text-3xl font-bold text-green-600">Healthy</p>
                        </div>
                    </div>

                    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center">
                        <h2 className="text-2xl font-bold text-slate-800 mb-4">Admin Features Coming Soon</h2>
                        <p className="text-slate-500 max-w-md mx-auto">
                            Advanced analytics, user management, and system configuration tools are currently under development.
                        </p>
                    </div>
                </main>
            </div>
        </ProtectedRoute>
    );
}
