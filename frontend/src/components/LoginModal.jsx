import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext';
import { X, User, Shield, Lock, ArrowRight, Loader2 } from 'lucide-react';

export default function LoginModal({ isOpen, onClose }) {
    const [activeTab, setActiveTab] = useState('manager'); // 'manager' or 'admin'
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const router = useRouter();

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const role = await login(email, password);
            
            // Verify role matches tab
            if (activeTab === 'admin' && role !== 'admin') {
                throw new Error("Access Denied: You are not an administrator.");
            }
            
            onClose();
            if (role === 'admin') {
                router.push('/admin/dashboard');
            } else {
                router.push('/hospital/dashboard');
            }
        } catch (err) {
            setError(err.message || "Login failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all scale-100">
                {/* Header */}
                <div className="flex justify-between items-center p-6 border-b border-slate-100">
                    <h2 className="text-xl font-bold text-slate-800">Sign In</h2>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex p-2 bg-slate-50 border-b border-slate-100">
                    <button
                        onClick={() => setActiveTab('manager')}
                        className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-medium rounded-lg transition-all ${
                            activeTab === 'manager' 
                                ? 'bg-white text-blue-600 shadow-sm' 
                                : 'text-slate-500 hover:text-slate-700'
                        }`}
                    >
                        <User className="w-4 h-4" /> Hospital Manager
                    </button>
                    <button
                        onClick={() => setActiveTab('admin')}
                        className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-medium rounded-lg transition-all ${
                            activeTab === 'admin' 
                                ? 'bg-white text-purple-600 shadow-sm' 
                                : 'text-slate-500 hover:text-slate-700'
                        }`}
                    >
                        <Shield className="w-4 h-4" /> Administrator
                    </button>
                </div>

                {/* Form */}
                <div className="p-6">
                    {error && (
                        <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-6 border border-red-100 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 bg-red-500 rounded-full"></span>
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                            <input
                                type="email"
                                required
                                className="w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all"
                                placeholder={activeTab === 'admin' ? "admin@axiom.com" : "manager@hospital.com"}
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
                            <div className="relative">
                                <input
                                    type="password"
                                    required
                                    className="w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                                <Lock className="absolute right-3 top-3 w-4 h-4 text-slate-400" />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full py-2.5 rounded-lg font-medium text-white transition-all flex items-center justify-center gap-2 ${
                                activeTab === 'admin' 
                                    ? 'bg-purple-600 hover:bg-purple-700 focus:ring-purple-100' 
                                    : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-100'
                            } focus:ring-4 disabled:opacity-70 disabled:cursor-not-allowed`}
                        >
                            {loading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>
                                    Sign In as {activeTab === 'manager' ? 'Manager' : 'Admin'}
                                    <ArrowRight className="w-4 h-4" />
                                </>
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
