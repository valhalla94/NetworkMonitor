import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import HostManager from './HostManager';
import { Lock, ArrowLeft, Eye, EyeOff, Bell, Save } from 'lucide-react';
import { getHosts, login, updateNotificationSettings, getSettings } from '../api';

const SettingsPage = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [hosts, setHosts] = useState([]);
    const [notificationUrl, setNotificationUrl] = useState('');
    const [notificationMsg, setNotificationMsg] = useState('');
    const navigate = useNavigate();

    const ADMIN_PASSWORD = import.meta.env.VITE_ADMIN_PASSWORD || 'admin';

    useEffect(() => {
        // Check if already authenticated in this session
        const token = sessionStorage.getItem('token');
        if (token) {
            setIsAuthenticated(true);
            setIsAuthenticated(true);
            fetchHosts();
            fetchSettings();
        }
    }, []);

    useEffect(() => {
        if (isAuthenticated) {
            fetchHosts();
            fetchSettings();
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

    const fetchSettings = async () => {
        try {
            const response = await getSettings();
            const notificationSetting = response.data.find(s => s.key === 'notification_url');
            if (notificationSetting) {
                setNotificationUrl(notificationSetting.value);
            }
        } catch (error) {
            console.error("Error fetching settings:", error);
        }
    };

    const handleSaveNotification = async (e) => {
        e.preventDefault();
        try {
            await updateNotificationSettings(notificationUrl);
            setNotificationMsg('Settings saved and test notification sent!');
            setTimeout(() => setNotificationMsg(''), 5000);
        } catch (error) {
            console.error("Error saving notification settings:", error);
            setNotificationMsg('Error saving settings.');
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

                {/* Notification Settings */}
                <div className="glass-panel p-8 rounded-2xl">
                    <h2 className="text-2xl font-bold mb-6 flex items-center gap-3 text-white">
                        <Bell className="text-amber-400" />
                        Notification Settings
                    </h2>
                    <div className="space-y-4 max-w-2xl">
                        <p className="text-slate-400">
                            Configure alerts using Apprise URLs. Supports Email, Slack, Discord, Telegram, and more.
                        </p>
                        <form onSubmit={handleSaveNotification} className="flex gap-4">
                            <div className="flex-1">
                                <label className="text-sm font-medium text-slate-300 ml-1 mb-1 block">Apprise URL</label>
                                <input
                                    type="text"
                                    value={notificationUrl}
                                    onChange={(e) => setNotificationUrl(e.target.value)}
                                    placeholder="e.g. discord://webhook_id/token"
                                    className="glass-input w-full px-4 py-2.5 rounded-xl outline-none font-mono text-sm"
                                />
                            </div>
                            <div className="flex items-end">
                                <button
                                    type="submit"
                                    className="glass-button px-6 py-2.5 rounded-xl font-bold text-lg flex items-center gap-2"
                                >
                                    <Save className="w-5 h-5" />
                                    Save & Test
                                </button>
                            </div>
                        </form>
                        {notificationMsg && (
                            <p className={`text-sm ${notificationMsg.includes('Error') ? 'text-rose-400' : 'text-emerald-400'} ml-1`}>
                                {notificationMsg}
                            </p>
                        )}
                        <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50 text-sm text-slate-400">
                            <p className="font-semibold text-slate-300 mb-2">Example URLs:</p>
                            <ul className="list-disc list-inside space-y-1 font-mono text-xs">
                                <li>discord://webhook_id/webhook_token</li>
                                <li>slack://tokenA/tokenB/tokenC</li>
                                <li>tgram://bot_token/chat_id</li>
                                <li>mailto://user:password@gmail.com</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsPage;
