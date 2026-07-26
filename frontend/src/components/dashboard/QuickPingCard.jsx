import React from 'react';
import { Search, Loader2, Play } from 'lucide-react';

const QuickPingCard = ({
    target,
    loading,
    result,
    onChangeTarget,
    onSubmitPing
}) => {
    return (
        <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-amber-500 bg-amber-900/10 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
                <Search className="w-20 h-20 text-amber-400" />
            </div>
            <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-full bg-amber-500/20 text-amber-400"><Search className="w-5 h-5" /></div>
                <h2 className="text-lg font-bold text-white">Quick Ping</h2>
            </div>
            <form onSubmit={onSubmitPing} className="flex gap-2 mb-4">
                <input type="text" value={target} onChange={(e) => onChangeTarget(e.target.value)}
                    placeholder="IP or Hostname" disabled={loading} aria-label="Quick ping target IP or hostname"
                    className="flex-1 bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-amber-500 focus-visible:ring-1 focus-visible:ring-amber-500 transition-colors disabled:opacity-50" />
                <button type="submit" disabled={loading || !target}
                    aria-label="Execute quick ping" title="Execute quick ping"
                    className="bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white px-3 py-2 rounded-lg transition-all flex items-center gap-1.5 font-medium cursor-pointer text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400">
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" /> : <Play className="w-4 h-4 fill-current" aria-hidden="true" />}
                </button>
            </form>
            {result && (
                <div className={`p-3 rounded-lg text-xs font-mono flex items-center justify-between border ${result.reachable ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20' : 'bg-rose-500/10 text-rose-300 border-rose-500/20'}`}>
                    <span>{result.target}</span>
                    <span>{result.reachable ? `${result.latency?.toFixed(1)}ms` : (result.error || 'Unreachable')}</span>
                </div>
            )}
        </div>
    );
};

export default React.memo(QuickPingCard);
