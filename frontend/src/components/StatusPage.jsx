import React, { useEffect, useState } from 'react';
import { getHosts, getNetworkStatus } from '../api';
import { Wifi, WifiOff, Server, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const StatusPage = () => {
    const [hosts, setHosts] = useState([]);
    const [networkStatus, setNetworkStatus] = useState({ status: 'UNKNOWN', reachable: 0, total: 0 });
    const [lastUpdated, setLastUpdated] = useState(new Date());

    const fetchData = async () => {
        try {
            const [hostsRes, statusRes] = await Promise.all([getHosts(), getNetworkStatus()]);
            setHosts(hostsRes.data);
            setNetworkStatus(statusRes.data);
            setLastUpdated(new Date());
        } catch (error) {
            console.error('Error fetching status:', error);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    const groups = hosts.reduce((acc, host) => {
        const group = host.group_name || 'General';
        if (!acc[group]) acc[group] = [];
        acc[group].push(host);
        return acc;
    }, {});

    const overallUp = networkStatus.status === 'UP';

    return (
        <div className="max-w-3xl mx-auto space-y-8 py-4">
            {/* Overall status banner */}
            <div className={`glass-panel p-8 rounded-2xl border-2 text-center ${overallUp ? 'border-emerald-500/50 bg-emerald-900/10' : 'border-rose-500/50 bg-rose-900/10'}`}>
                <div className={`inline-flex p-4 rounded-full mb-4 ${overallUp ? 'bg-emerald-500/20' : 'bg-rose-500/20'}`}>
                    {overallUp ? <Wifi className="w-10 h-10 text-emerald-400" /> : <WifiOff className="w-10 h-10 text-rose-400" />}
                </div>
                <h1 className="text-4xl font-bold text-white mb-2">
                    {overallUp ? 'All Systems Operational' : 'Service Disruption'}
                </h1>
                <p className="text-slate-400">
                    {networkStatus.reachable}/{networkStatus.total} services reachable
                </p>
                <p className="text-slate-500 text-sm mt-3">
                    Last updated {formatDistanceToNow(lastUpdated, { addSuffix: true })}
                </p>
            </div>

            {/* Per-group status */}
            {Object.entries(groups).map(([groupName, groupHosts]) => (
                <div key={groupName} className="glass-panel rounded-2xl overflow-hidden">
                    <div className="px-6 py-4 border-b border-slate-700/50 flex items-center justify-between">
                        <h2 className="text-lg font-bold text-white capitalize">{groupName}</h2>
                        <span className="text-xs text-slate-500">{groupHosts.filter(h => h.last_status === 'UP').length}/{groupHosts.length} up</span>
                    </div>
                    <div className="divide-y divide-slate-700/50">
                        {groupHosts.map(host => {
                            const isUp = host.last_status === 'UP';
                            const isMaint = host.maintenance;
                            return (
                                <div key={host.id} className="px-6 py-4 flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <Server className="w-4 h-4 text-slate-500 flex-shrink-0" />
                                        <div>
                                            <div className="font-medium text-white">{host.name}</div>
                                            <div className="text-xs text-slate-500 font-mono">{host.ip_address}</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {host.average_latency && (
                                            <span className="text-xs text-slate-500 font-mono">{host.average_latency.toFixed(1)}ms</span>
                                        )}
                                        {isMaint ? (
                                            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 text-xs font-medium">
                                                <AlertTriangle className="w-3.5 h-3.5" />Maintenance
                                            </span>
                                        ) : isUp ? (
                                            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-medium">
                                                <CheckCircle className="w-3.5 h-3.5" />Operational
                                            </span>
                                        ) : (
                                            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/20 text-rose-400 text-xs font-medium">
                                                <XCircle className="w-3.5 h-3.5" />Down
                                            </span>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            ))}

            {hosts.length === 0 && (
                <div className="text-center text-slate-500 py-12">No hosts configured.</div>
            )}
        </div>
    );
};

export default StatusPage;
