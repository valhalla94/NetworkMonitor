import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import HostManager from './HostManager';
import { Lock, ArrowLeft, Eye, EyeOff } from 'lucide-react';
import { getHosts, login } from '../api';

const SettingsPage = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [hosts, setHosts] = useState([]);
    const navigate = useNavigate();

    const ADMIN_PASSWORD = import.meta.env.VITE_ADMIN_PASSWORD || 'admin';

    useEffect(() => {
        // Check if already authenticated in this session
        const token = sessionStorage.getItem('token');
        if (token) {
            setIsAuthenticated(true);
            fetchHosts();
        }
    }, []);

    useEffect(() => {
        if (isAuthenticated) {
            fetchHosts();
        }
    }, [isAuthenticated]);

    const fetchHosts = async () => {
        try {
            const response = await getHosts();
            setHosts(response.data);
        } catch (error) {
            console.error("Error fetching hosts:", error);
        }
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await login('admin', password);
            sessionStorage.setItem('token', response.data.access_token);
            setIsAuthenticated(true);
            setError('');
            setPassword('');
        } catch (err) {
            setError('Incorrect password');
            setPassword('');
        }
    };

    const handleLogout = () => {
        setIsAuthenticated(false);
        sessionStorage.removeItem('token');
        navigate('/');
    };

    if (!isAuthenticated) {
        return (
            <div className="min-h-screen flex items-center justify-center p-4">
                <div className="glass-panel p-8 rounded-2xl w-full max-w-md">
                    <div className="text-center mb-8">
                        <div className="inline-flex p-4 bg-blue-500/10 rounded-full mb-4">
                            <Lock className="w-8 h-8 text-blue-400" />
                        </div>
                        <h2 className="text-3xl font-bold text-white mb-2">Settings Access</h2>
                        <p className="text-slate-400">Enter password to manage host settings</p>
                    </div>

                    <form onSubmit={handleLogin} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300 ml-1">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                                <input
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="glass-input w-full pl-10 pr-12 py-2.5 rounded-xl outline-none"
                                    placeholder="Enter password"
                                    required
                                    autoFocus
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-3 text-slate-500 hover:text-slate-300 transition-colors"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                            {error && (
                                <p className="text-rose-400 text-sm ml-1 mt-2">{error}</p>
                            )}
                        </div>

                        <div className="space-y-3">
                            <button
                                type="submit"
                                className="glass-button w-full py-3 rounded-xl font-bold text-lg flex items-center justify-center gap-2"
                            >
                                <Lock className="w-5 h-5" />
                                Unlock Settings
                            </button>
                            <button
                                type="button"
                                onClick={() => navigate('/')}
                                className="w-full py-3 rounded-xl font-medium text-slate-300 hover:text-white hover:bg-slate-800/30 transition-all flex items-center justify-center gap-2"
                            >
                                <ArrowLeft className="w-5 h-5" />
                                Back to Dashboard
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen p-4 md:p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-bold text-white">Host Settings</h1>
                    <div className="flex gap-3">
                        <button
                            onClick={() => navigate('/')}
                            className="px-4 py-2 rounded-xl font-medium text-slate-300 hover:text-white hover:bg-slate-800/30 transition-all flex items-center gap-2"
                        >
                            <ArrowLeft className="w-5 h-5" />
                            Dashboard
                        </button>
                        <button
                            onClick={handleLogout}
                            className="px-4 py-2 rounded-xl font-medium bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 transition-all flex items-center gap-2"
                        >
                            <Lock className="w-5 h-5" />
                            Logout
                        </button>
                    </div>
                </div>
                <HostManager
                    onHostAdded={fetchHosts}
                    onHostDeleted={fetchHosts}
                    hosts={hosts}
                />
            </div>
        </div>
    );
};

export default SettingsPage;
