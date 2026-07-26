import React from 'react';
import { Globe, Timer, Clock } from 'lucide-react';
import { format } from 'date-fns';

const PublicIpCard = ({ publicIpHistory, ipStats }) => {
    const hasHistory = publicIpHistory.length > 0;
    const currentIp = hasHistory ? publicIpHistory[0].ip_address : '—';
    const lastChecked = hasHistory ? format(new Date(publicIpHistory[0].time), 'HH:mm:ss') : '-';

    return (
        <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-blue-500 bg-blue-900/10 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
                <Globe className="w-20 h-20 text-blue-400" />
            </div>
            <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-full bg-blue-500/20 text-blue-400"><Globe className="w-5 h-5" /></div>
                <h2 className="text-lg font-bold text-white">Public IP</h2>
                {ipStats.duration && (
                    <div className="ml-auto px-3 py-1 rounded-full bg-blue-500/20 border border-blue-500/30 text-blue-300 text-xs flex items-center gap-1.5">
                        <Timer className="w-3.5 h-3.5" />{ipStats.duration}
                    </div>
                )}
            </div>
            <div className="text-2xl md:text-3xl font-mono font-bold text-white tracking-wider mb-1">
                {currentIp}
            </div>
            <div className="text-xs text-slate-400 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                Last checked: {lastChecked}
            </div>
            {ipStats.since && (
                <div className="mt-3 pt-3 border-t border-slate-700/50 text-xs text-blue-200">
                    Active since {format(new Date(ipStats.since), 'MMM d, yyyy • HH:mm')}
                </div>
            )}
        </div>
    );
};

export default React.memo(PublicIpCard);
