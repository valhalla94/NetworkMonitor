import React from 'react';
import { Wifi, WifiOff } from 'lucide-react';

const NetworkStatusBanner = ({ networkStatus }) => {
    const isUp = networkStatus.status === 'UP';

    return (
        <div className={`lg:col-span-2 glass-panel p-6 md:p-8 rounded-2xl border-l-4 ${isUp ? 'border-l-emerald-500 bg-emerald-900/10' : 'border-l-rose-500 bg-rose-900/10'}`}>
            <div className="flex items-center gap-4 md:gap-6">
                <div className={`p-3 md:p-4 rounded-full flex-shrink-0 ${isUp ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                    {isUp ? <Wifi className="w-6 h-6 md:w-8 md:h-8" /> : <WifiOff className="w-6 h-6 md:w-8 md:h-8" />}
                </div>
                <div>
                    <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-white">System Status: {networkStatus.status}</h2>
                    <p className="text-slate-400 mt-1">Reachable: <span className="text-white font-medium">{networkStatus.reachable}</span> / {networkStatus.total}</p>
                </div>
            </div>
        </div>
    );
};

export default React.memo(NetworkStatusBanner);
