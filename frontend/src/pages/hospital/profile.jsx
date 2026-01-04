import React from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import { useAuth } from '../../context/AuthContext';
import { Building2, MapPin, Clock, Stethoscope, ArrowRight } from 'lucide-react';
import { useRouter } from 'next/router';

export default function HospitalProfile() {
    const { user, logout } = useAuth();
    const router = useRouter();

    if (!user) return null;

    return (
        <ProtectedRoute allowedRoles={['hospital', 'admin']}>
            <div className="min-h-screen bg-slate-50">
                {/* Header */}
                <header className="bg-white border-b px-8 py-6 sticky top-0 z-10">
                    <div className="max-w-6xl mx-auto flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <div className="bg-blue-600 p-2 rounded-lg">
                                <Building2 className="text-white w-6 h-6" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-slate-800 leading-none">{user.hospital_name}</h1>
                                <div className="flex items-center gap-1 text-slate-500 text-sm mt-1">
                                    <MapPin className="w-3 h-3" /> {user.location || 'Location not set'}
                                </div>
                            </div>
                        </div>
                        <div className="flex gap-4">
                             <button 
                                onClick={() => router.push('/')}
                                className="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg font-medium hover:bg-blue-100 transition-colors"
                            >
                                Dashboard
                            </button>
                            <button 
                                onClick={logout}
                                className="px-4 py-2 text-slate-500 hover:text-slate-800 font-medium transition-colors"
                            >
                                Sign Out
                            </button>
                        </div>
                    </div>
                </header>

                <main className="max-w-6xl mx-auto p-8 space-y-8">
                    {/* Welcome Section */}
                    <section className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
                        <h2 className="text-xl font-bold text-slate-800 mb-2">Hospital Overview</h2>
                        <p className="text-slate-600">
                            Welcome to the AxiomForage command center. Manage your hospital's resources, view predictive analytics, and ensure optimal patient care.
                        </p>
                    </section>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {/* Services Card */}
                        <div className="md:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                            <div className="flex items-center gap-3 mb-6">
                                <Stethoscope className="text-blue-600 w-5 h-5" />
                                <h3 className="text-lg font-bold text-slate-800">Available Services</h3>
                            </div>
                            
                            {user.services && user.services.length > 0 ? (
                                <div className="grid grid-cols-2 gap-4">
                                    {user.services.map((service, index) => (
                                        <div key={index} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                                            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                            <span className="font-medium text-slate-700">{service}</span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-8 text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                                    No services listed yet.
                                </div>
                            )}
                        </div>

                        {/* Timings Card */}
                        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                            <div className="flex items-center gap-3 mb-6">
                                <Clock className="text-orange-500 w-5 h-5" />
                                <h3 className="text-lg font-bold text-slate-800">Operating Hours</h3>
                            </div>

                            <div className="space-y-4">
                                {user.timings && Object.keys(user.timings).length > 0 ? (
                                    Object.entries(user.timings).map(([day, time]) => (
                                        <div key={day} className="flex justify-between items-center pb-3 border-b border-slate-50 last:border-0">
                                            <span className="text-slate-500 font-medium capitalize">{day}</span>
                                            <span className="text-slate-800 font-semibold">{time}</span>
                                        </div>
                                    ))
                                ) : (
                                    <div className="text-center py-8 text-slate-400">
                                        Standard 24/7 Operations
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </ProtectedRoute>
    );
}
