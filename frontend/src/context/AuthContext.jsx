import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/router';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        // Check for token on mount
        const token = localStorage.getItem('token');
        if (token) {
            fetchProfile(token);
        } else {
            setLoading(false);
        }
    }, []);

    const fetchProfile = async (token) => {
        try {
            const response = await fetch('http://127.0.0.1:8001/api/v1/auth/me', {
                headers: { Authorization: `Bearer ${token}` }
            });
            
            if (response.ok) {
                const userData = await response.json();
                setUser(userData);
                setLoading(false);
                return userData;
            } else {
                logout();
            }
        } catch (error) {
            console.error("Auth check failed:", error);
            logout();
        }
        setLoading(false);
        return null;
    };

    const login = async (email, password) => {
        try {
            const response = await fetch('http://127.0.0.1:8001/api/v1/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }

            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            const userProfile = await fetchProfile(data.access_token);
            
            return userProfile?.role;
        } catch (error) {
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
        router.push('/login');
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading, isAuthenticated: !!user }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
