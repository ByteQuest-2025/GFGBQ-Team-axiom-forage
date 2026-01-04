import React, { useState } from 'react';
import { BrainCircuit, Activity, Shield, ArrowRight, CheckCircle2 } from 'lucide-react';
import LoginModal from '../components/LoginModal';
import { useAuth } from '../context/AuthContext';
import { useRouter } from 'next/router';

export default function LandingPage() {
    const [isLoginOpen, setIsLoginOpen] = useState(false);
    const { user, isAuthenticated } = useAuth();
    const router = useRouter();

    const handleDashboardClick = () => {
        if (user?.role === 'admin') {
            router.push('/admin/dashboard');
        } else {
            router.push('/hospital/dashboard');
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 font-sans">
            {/* Navigation */}
            <nav className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40">
                <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <div className="bg-blue-600 p-2 rounded-lg shadow-lg shadow-blue-200">
                            <BrainCircuit className="text-white w-6 h-6" />
                        </div>
                        <span className="text-xl font-bold text-slate-800 tracking-tight">
                            AxiomForage <span className="text-blue-600">HealthAI</span>
                        </span>
                    </div>
                    
                    <div className="flex items-center gap-4">
                        {isAuthenticated ? (
                            <button 
                                onClick={handleDashboardClick}
                                className="bg-slate-900 hover:bg-slate-800 text-white px-5 py-2.5 rounded-lg font-medium transition-all flex items-center gap-2"
                            >
                                Go to Dashboard <ArrowRight className="w-4 h-4" />
                            </button>
                        ) : (
                            <button 
                                onClick={() => setIsLoginOpen(true)}
                                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-medium transition-all shadow-lg shadow-blue-200 hover:shadow-blue-300"
                            >
                                Login
                            </button>
                        )}
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="max-w-7xl mx-auto px-6 py-20 lg:py-32">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                    <div className="space-y-8">
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm font-medium border border-blue-100">
                            <Activity className="w-4 h-4" /> AI-Powered Hospital Management
                        </div>
                        
                        <h1 className="text-5xl lg:text-6xl font-bold text-slate-900 leading-tight">
                            Predictive Intelligence for <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Critical Care</span>
                        </h1>
                        
                        <p className="text-xl text-slate-600 leading-relaxed">
                            Optimize ER and ICU resources with real-time predictive analytics. 
                            Anticipate patient surges, manage staff allocation, and ensure 
                            operational readiness before the crisis hits.
                        </p>

                        <div className="flex flex-col sm:flex-row gap-4 pt-4">
                            <button 
                                onClick={() => setIsLoginOpen(true)}
                                className="px-8 py-4 bg-slate-900 text-white rounded-xl font-bold text-lg hover:bg-slate-800 transition-all shadow-xl hover:shadow-2xl hover:-translate-y-1 flex items-center justify-center gap-2"
                            >
                                Get Started <ArrowRight className="w-5 h-5" />
                            </button>
                            <button className="px-8 py-4 bg-white text-slate-700 border border-slate-200 rounded-xl font-bold text-lg hover:bg-slate-50 transition-all flex items-center justify-center gap-2">
                                View Demo
                            </button>
                        </div>

                        <div className="pt-8 grid grid-cols-2 gap-6">
                            <div className="flex items-center gap-3 text-slate-600">
                                <CheckCircle2 className="text-green-500 w-5 h-5" /> 94% Accuracy
                            </div>
                            <div className="flex items-center gap-3 text-slate-600">
                                <CheckCircle2 className="text-green-500 w-5 h-5" /> Real-time Sync
                            </div>
                            <div className="flex items-center gap-3 text-slate-600">
                                <CheckCircle2 className="text-green-500 w-5 h-5" /> HIPAA Compliant
                            </div>
                            <div className="flex items-center gap-3 text-slate-600">
                                <CheckCircle2 className="text-green-500 w-5 h-5" /> 24/7 Monitoring
                            </div>
                        </div>
                    </div>

                    <div className="relative">
                        <div className="absolute -inset-4 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full blur-3xl opacity-50 animate-pulse-slow"></div>
                        <div className="relative bg-white p-8 rounded-3xl shadow-2xl border border-slate-100">
                            <div className="flex items-center justify-between mb-8">
                                <div className="space-y-1">
                                    <h3 className="font-bold text-slate-800">Live System Status</h3>
                                    <p className="text-sm text-slate-500">Apollo Jubilee Hills</p>
                                </div>
                                <div className="flex items-center gap-2 px-3 py-1 bg-green-50 text-green-700 rounded-full text-xs font-bold border border-green-100">
                                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                    OPERATIONAL
                                </div>
                            </div>
                            
                            <div className="space-y-6">
                                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="text-slate-500">ICU Occupancy</span>
                                        <span className="font-bold text-slate-800">82%</span>
                                    </div>
                                    <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                                        <div className="h-full bg-amber-500 w-[82%]"></div>
                                    </div>
                                </div>

                                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="text-slate-500">ER Wait Time</span>
                                        <span className="font-bold text-slate-800">12 min</span>
                                    </div>
                                    <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                                        <div className="h-full bg-blue-500 w-[30%]"></div>
                                    </div>
                                </div>

                                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="text-slate-500">Staff Availability</span>
                                        <span className="font-bold text-slate-800">High</span>
                                    </div>
                                    <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                                        <div className="h-full bg-green-500 w-[90%]"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Login Modal */}
            <LoginModal isOpen={isLoginOpen} onClose={() => setIsLoginOpen(false)} />
        </div>
    );
}

// hi i doesnt change 