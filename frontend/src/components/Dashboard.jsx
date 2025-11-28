import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getHosts, getMetrics, getNetworkStatus, getPublicIpHistory, getSpeedTestHistory, runSpeedTest } from '../api';
import { Activity, Server, Wifi, WifiOff, Clock, Calendar, Globe, History, Timer, Gauge, ArrowDown, ArrowUp, Play, Loader2 } from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';

const Dashboard = () => {
    const [hosts, setHosts] = useState([]);
    const [selectedHost, setSelectedHost] = useState(null);
    const [metrics, setMetrics] = useState([]);
    const [uptime, setUptime] = useState(0);
    const [avgLatency, setAvgLatency] = useState(0);
    const [timeRange, setTimeRange] = useState('-1h');
    const [networkStatus, setNetworkStatus] = useState({ status: 'UNKNOWN', reachable: 0, total: 0 });
    const [publicIpHistory, setPublicIpHistory] = useState([]);
    const [ipStats, setIpStats] = useState({ since: null, duration: null });
    const [speedTestHistory, setSpeedTestHistory] = useState([]);
    const [isSpeedTestRunning, setIsSpeedTestRunning] = useState(false);
    const [isChartLoading, setIsChartLoading] = useState(false);

    useEffect(() => {
        fetchHosts();
        fetchNetworkStatus();
        fetchPublicIpHistory();
        fetchSpeedTestHistory();
        const interval = setInterval(() => {
            fetchHosts();
            fetchNetworkStatus();
        }, 30000);

        // Check public IP history less frequently, e.g., every 5 minutes
        const ipInterval = setInterval(fetchPublicIpHistory, 300000);

        return () => {
            clearInterval(interval);
            clearInterval(ipInterval);
        };
    }, []);

    useEffect(() => {
        if (publicIpHistory.length > 0) {
            const currentIp = publicIpHistory[0].ip_address;
            let since = publicIpHistory[0].time;

            // Find the oldest consecutive record with the same IP
            for (let i = 1; i < publicIpHistory.length; i++) {
                if (publicIpHistory[i].ip_address === currentIp) {
                    since = publicIpHistory[i].time;
                } else {
                    break;
                }
            }

            setIpStats({
                since: since,
                duration: formatDistanceToNow(new Date(since))
            });
        }
    }, [publicIpHistory]);

    useEffect(() => {
        if (selectedHost) {
            fetchMetrics(selectedHost.id);
            const interval = setInterval(() => fetchMetrics(selectedHost.id), 10000);
            return () => clearInterval(interval);
        }
    }, [selectedHost, timeRange]);

    const fetchHosts = async () => {
        try {
            const response = await getHosts();
            setHosts(response.data);
            if (!selectedHost && response.data.length > 0) {
                setSelectedHost(response.data[0]);
            }
        } catch (error) {
            console.error("Error fetching hosts:", error);
        }
    };

    const fetchNetworkStatus = async () => {
        try {
            const response = await getNetworkStatus();
            setNetworkStatus(response.data);
        } catch (error) {
            console.error("Error fetching network status:", error);
        }
    };

    const fetchPublicIpHistory = async () => {
        try {
            const response = await getPublicIpHistory();
            setPublicIpHistory(response.data);
        } catch (error) {
            console.error("Error fetching public IP history:", error);
        }
    };

    const fetchSpeedTestHistory = async () => {
        try {
            const response = await getSpeedTestHistory();
            setSpeedTestHistory(response.data);
        } catch (error) {
            console.error("Error fetching speed test history:", error);
        }
    };

    const handleRunSpeedTest = async () => {
        setIsSpeedTestRunning(true);
        try {
            await runSpeedTest();
            // The test runs in the background and takes about 30-60s.
            // We'll keep the button in a "running" state for 60s to give feedback.
            setTimeout(() => {
                setIsSpeedTestRunning(false);
                fetchSpeedTestHistory(); // Refresh results after waiting
            }, 60000);
        } catch (error) {
            console.error("Error starting speed test:", error);
            alert("Failed to start speed test");
            setIsSpeedTestRunning(false);
        }
    };

    const fetchMetrics = async (hostId) => {
        setIsChartLoading(true);
        try {
            const response = await getMetrics(hostId, timeRange);
            const formattedData = response.data.data.map(d => ({
                ...d,
                time: new Date(d.time).toLocaleString(), // Show full date for long ranges
                latency: Math.round(d.latency * 100) / 100
            }));
            setMetrics(formattedData);
            setUptime(response.data.uptime);
            setAvgLatency(response.data.avg_latency);
        } catch (error) {
            console.error("Error fetching metrics:", error);
        } finally {
            setIsChartLoading(false);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Network Status Card */}
                <div className={`lg:col-span-2 glass-panel p-8 rounded-2xl border-l-4 ${networkStatus.status === 'UP' ? 'border-l-emerald-500 bg-emerald-900/10' : 'border-l-rose-500 bg-rose-900/10'}`}>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-6">
                            <div className={`p-4 rounded-full ${networkStatus.status === 'UP' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                                {networkStatus.status === 'UP' ? <Wifi className="w-8 h-8" /> : <WifiOff className="w-8 h-8" />}
                            </div>
                            <div>
                                <h2 className="text-3xl font-bold tracking-tight text-white">System Status: {networkStatus.status}</h2>
                                <p className="text-slate-400 mt-1 text-lg">Reachable Hosts: <span className="text-white font-medium">{networkStatus.reachable}</span> / {networkStatus.total}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Public IP Card */}
                <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-blue-500 bg-blue-900/10 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Globe className="w-24 h-24 text-blue-400" />
                    </div>

                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-full bg-blue-500/20 text-blue-400">
                                <Globe className="w-5 h-5" />
                            </div>
                            <h2 className="text-lg font-bold text-white">Public IP</h2>
                        </div>
                        {ipStats.duration && (
                            <div className="px-3 py-1 rounded-full bg-blue-500/20 border border-blue-500/30 text-blue-300 text-xs font-medium flex items-center gap-1.5">
                                <Timer className="w-3.5 h-3.5" />
                                {ipStats.duration}
                            </div>
                        )}
                    </div>

                    <div className="mb-6">
                        <div className="text-4xl font-mono font-bold text-white tracking-wider mb-2">
                            {publicIpHistory.length > 0 ? publicIpHistory[0].ip_address : 'Loading...'}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-slate-400">
                            <div className="flex items-center gap-1.5">
                                <Clock className="w-3.5 h-3.5" />
                                <span className="text-xs">Last checked: {publicIpHistory.length > 0 ? format(new Date(publicIpHistory[0].time), 'HH:mm:ss') : '-'}</span>
                            </div>
                        </div>
                    </div>

                    {ipStats.since && (
                        <div className="pt-4 border-t border-slate-700/50">
                            <div className="flex items-center gap-2">
                                <div className="p-1.5 rounded bg-slate-800 text-slate-400">
                                    <History className="w-3.5 h-3.5" />
                                </div>
                                <div>
                                    <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold">IP Active Since</div>
                                    <div className="text-sm font-medium text-blue-200">
                                        {format(new Date(ipStats.since), 'MMMM d, yyyy • HH:mm')}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Speed Test Card */}
                <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-violet-500 bg-violet-900/10 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Gauge className="w-24 h-24 text-violet-400" />
                    </div>

                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-full bg-violet-500/20 text-violet-400">
                                <Gauge className="w-5 h-5" />
                            </div>
                            <h2 className="text-lg font-bold text-white">Internet Speed</h2>
                        </div>
                        <button
                            onClick={handleRunSpeedTest}
                            disabled={isSpeedTestRunning}
                            className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all shadow-lg ${isSpeedTestRunning
                                    ? 'bg-violet-500/10 border border-violet-500/20 text-violet-400 cursor-not-allowed'
                                    : 'bg-violet-600 hover:bg-violet-500 text-white shadow-violet-500/20 hover:shadow-violet-500/40 border border-transparent'
                                }`}
                        >
                            {isSpeedTestRunning ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    <span>Test Running...</span>
                                </>
                            ) : (
                                <>
                                    <Play className="w-4 h-4 fill-current" />
                                    <span>Run Speed Test</span>
                                </>
                            )}
                        </button>
                    </div>

                    <div className="mb-6 grid grid-cols-2 gap-4">
                        <div>
                            <div className="text-xs text-slate-400 mb-1 flex items-center gap-1">
                                <ArrowDown className="w-3 h-3" /> Download
                            </div>
                            <div className="text-2xl font-mono font-bold text-white tracking-wider">
                                {speedTestHistory.length > 0 ? speedTestHistory[0].download.toFixed(1) : '-'} <span className="text-sm text-slate-500">Mbps</span>
                            </div>
                        </div>
                        <div>
                            <div className="text-xs text-slate-400 mb-1 flex items-center gap-1">
                                <ArrowUp className="w-3 h-3" /> Upload
                            </div>
                            <div className="text-2xl font-mono font-bold text-white tracking-wider">
                                {speedTestHistory.length > 0 ? speedTestHistory[0].upload.toFixed(1) : '-'} <span className="text-sm text-slate-500">Mbps</span>
                            </div>
                        </div>
                    </div>

                    <div className="pt-4 border-t border-slate-700/50">
                        <div className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2 text-slate-400">
                                <Activity className="w-3.5 h-3.5" />
                                <span>Ping: <span className="text-white font-mono">{speedTestHistory.length > 0 ? speedTestHistory[0].ping.toFixed(0) : '-'}ms</span></span>
                            </div>
                            <div className="text-xs text-slate-500">
                                {speedTestHistory.length > 0 ? formatDistanceToNow(new Date(speedTestHistory[0].timestamp), { addSuffix: true }) : 'No data'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Host Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {hosts.map(host => (
                    <div
                        key={host.id}
                        onClick={() => setSelectedHost(host)}
                        className={`glass-panel p-6 rounded-2xl cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl group ${selectedHost?.id === host.id ? 'ring-2 ring-blue-500/50 bg-slate-800/60' : 'hover:bg-slate-800/60'}`}
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                                <div className="p-3 rounded-xl bg-blue-500/10 text-blue-400 group-hover:bg-blue-500/20 transition-colors">
                                    <Server className="w-6 h-6" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg text-white group-hover:text-blue-400 transition-colors">{host.name}</h3>
                                    <p className="text-sm text-slate-400 font-mono">
                                        {host.ip_address}
                                        {host.port && <span className="text-slate-500 ml-1">:{host.port}</span>}
                                    </p>
                                    {host.average_latency !== null && (
                                        <p className="text-xs text-slate-500 mt-1">
                                            Avg (6h): <span className="text-blue-300 font-medium">{host.average_latency.toFixed(2)}ms</span>
                                        </p>
                                    )}
                                </div>
                            </div>
                            <div className={`w-3 h-3 rounded-full shadow-lg shadow-current ${host.enabled ? 'bg-emerald-400 text-emerald-400' : 'bg-rose-400 text-rose-400'}`}></div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Metrics Chart */}
                {/* Metrics Chart */}
                {selectedHost && (
                    <div className="lg:col-span-2 glass-panel p-8 rounded-2xl relative">
                        {isChartLoading && (
                            <div className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm z-10 flex items-center justify-center rounded-2xl">
                                <div className="flex flex-col items-center gap-3">
                                    <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                                    <span className="text-blue-400 font-medium animate-pulse">Loading data...</span>
                                </div>
                            </div>
                        )}

                        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-6">
                            <div>
                                <h2 className="text-2xl font-bold flex items-center gap-3 text-white">
                                    <Activity className="text-blue-400 w-6 h-6" />
                                    {selectedHost.name}
                                </h2>
                                <p className="text-slate-400 mt-2 flex items-center gap-2">
                                    Uptime:
                                    <span className={`font-bold px-2 py-0.5 rounded-md ${uptime >= 99 ? 'bg-emerald-500/20 text-emerald-400' : uptime >= 90 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-rose-500/20 text-rose-400'}`}>
                                        {uptime.toFixed(2)}%
                                    </span>
                                    <span className="ml-4">Avg Latency:</span>
                                    <span className="font-bold px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-400">
                                        {avgLatency.toFixed(2)}ms
                                    </span>
                                </p>
                            </div>

                            <div className="flex items-center gap-2 bg-slate-900/50 p-1 rounded-xl border border-slate-700/50">
                                {[
                                    { label: '1H', value: '-1h' },
                                    { label: '6H', value: '-6h' },
                                    { label: '24H', value: '-24h' },
                                    { label: '7D', value: '-7d' },
                                    { label: '30D', value: '-30d' },
                                    { label: '1Y', value: '-1y' },
                                    { label: '2Y', value: '-2y' },
                                ].map((option) => (
                                    <button
                                        key={option.value}
                                        onClick={() => setTimeRange(option.value)}
                                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${timeRange === option.value ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
                                    >
                                        {option.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="h-[500px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={metrics}>
                                    <defs>
                                        <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                    <XAxis
                                        dataKey="time"
                                        stroke="#94a3b8"
                                        tick={{ fill: '#94a3b8' }}
                                        tickLine={false}
                                        axisLine={false}
                                        minTickGap={50}
                                    />
                                    <YAxis
                                        stroke="#94a3b8"
                                        unit="ms"
                                        tick={{ fill: '#94a3b8' }}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                                            backdropFilter: 'blur(8px)',
                                            borderColor: '#334155',
                                            color: '#f1f5f9',
                                            borderRadius: '12px',
                                            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)'
                                        }}
                                        itemStyle={{ color: '#60a5fa' }}
                                        animationDuration={300}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="latency"
                                        stroke="#3b82f6"
                                        strokeWidth={3}
                                        fillOpacity={1}
                                        fill="url(#colorLatency)"
                                        animationDuration={500}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}

                {/* Public IP History List */}
                <div className="glass-panel p-6 rounded-2xl overflow-hidden flex flex-col h-[650px]">
                    <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                        <Clock className="w-5 h-5 text-blue-400" />
                        IP History
                    </h3>
                    <div className="overflow-y-auto pr-2 space-y-3 custom-scrollbar flex-1">
                        {publicIpHistory.map((record, index) => (
                            <div key={index} className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50 flex justify-between items-center">
                                <span className="font-mono text-blue-300">{record.ip_address}</span>
                                <span className="text-xs text-slate-500">{new Date(record.time).toLocaleString()}</span>
                            </div>
                        ))}
                        {publicIpHistory.length === 0 && (
                            <div className="text-center text-slate-500 py-8">
                                No history available
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
