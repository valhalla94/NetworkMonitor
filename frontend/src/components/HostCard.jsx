import React from 'react';
import { Server, Lock } from 'lucide-react';

const HostCard = React.memo(({ host, isSelected, onSelect }) => {
    return (
        <div onClick={() => onSelect(host)}
            className={`glass-panel p-5 rounded-2xl cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl group relative overflow-hidden ${isSelected ? 'ring-2 ring-blue-500/50 bg-slate-800/60' : 'hover:bg-slate-800/60'}`}>
            {host.maintenance && (
                <div className="absolute top-0 right-0 bg-amber-500/90 text-slate-900 text-[10px] font-bold px-4 py-1 rotate-45 translate-x-3 translate-y-2 shadow-lg z-10 w-24 text-center">MAINT</div>
            )}
            <div className={`flex items-center justify-between ${host.maintenance ? 'opacity-70' : ''}`}>
                <div className="flex items-center space-x-3">
                    <div className={`p-2.5 rounded-xl ${host.maintenance ? 'bg-amber-500/10 text-amber-400' : 'bg-blue-500/10 text-blue-400 group-hover:bg-blue-500/20'}`}>
                        <Server className="w-5 h-5" />
                    </div>
                    <div>
                        <h3 className="font-bold text-white group-hover:text-blue-400 transition-colors">{host.name}</h3>
                        <p className="text-xs text-slate-400 font-mono">{host.ip_address}{host.port ? `:${host.port}` : ''}</p>
                        {host.average_latency !== null && (
                            <p className="text-xs text-slate-500 mt-0.5">Avg: <span className="text-blue-300">{host.average_latency?.toFixed(2)}ms</span></p>
                        )}
                        <div className="flex flex-wrap gap-1 mt-1">
                            {host.monitor_type === 'tcp' && <span className="text-[10px] px-1.5 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/20">TCP:{host.port}</span>}
                            {host.monitor_type === 'http' && <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">HTTP</span>}
                            {host.monitor_type === 'heartbeat' && <span className="text-[10px] px-1.5 py-0.5 rounded bg-pink-500/10 text-pink-400 border border-pink-500/20">💓 HB</span>}
                            {host.ssl_monitor && <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-0.5"><Lock className="w-2.5 h-2.5" />SSL</span>}
                            {host.latency_threshold_ms && <span className="text-[10px] px-1.5 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/20">⚡{host.latency_threshold_ms}ms</span>}
                        </div>
                    </div>
                </div>
                <div className={`w-3 h-3 rounded-full flex-shrink-0 shadow-lg ${host.maintenance ? 'bg-amber-400' : host.last_status === 'UP' ? 'bg-emerald-400 shadow-emerald-400/50' : host.last_status === 'DOWN' ? 'bg-rose-400 shadow-rose-400/50' : 'bg-slate-400'}`} />
            </div>
        </div>
    );
});

HostCard.displayName = 'HostCard';

export default HostCard;
