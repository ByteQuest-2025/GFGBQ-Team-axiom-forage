import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext';
import { RefreshCw } from 'lucide-react';

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
    const { user, loading, isAuthenticated } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!loading && !isAuthenticated) {
            router.push('/login');
        }
        
        if (!loading && isAuthenticated && allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
            // Redirect based on role if unauthorized for current page
            if (user.role === 'admin') router.push('/admin/dashboard');
            else router.push('/hospital/profile');
        }
    }, [loading, isAuthenticated, user, router, allowedRoles]);

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center bg-slate-50">
                <RefreshCw className="animate-spin w-8 h-8 text-blue-600" />
            </div>
        );
    }

    if (!isAuthenticated) return null;

    return children;
};

export default ProtectedRoute;
