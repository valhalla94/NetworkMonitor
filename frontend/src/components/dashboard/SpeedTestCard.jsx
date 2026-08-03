import React from 'react';
import { Gauge, Play, Loader2, ArrowDown, ArrowUp } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const SpeedTestCard = ({ speedTestHistory, isSpeedTestRunning, onRunSpeedTest }) => {
    const hasHistory = speedTestHistory.length > 0;
    const download = hasHistory ? speedTestHistory[0].download.toFixed(1) : '-';
    const upload = hasHistory ? speedTestHistory[0].upload.toFixed(1) : '-';
    const ping = hasHistory ? speedTestHistory[0].ping.toFixed(0) : '-';
    const timeAgo = hasHistory ? formatDistanceToNow(new Date(speedTestHistory[0].timestamp), { addSuffix: true }) : 'No data';

    return (
        <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-violet-500 bg-violet-900/10 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
                <Gauge className="w-20 h-20 text-violet-400" />
            </div>
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-full bg-violet-500/20 text-violet-400"><Gauge className="w-5 h-5" /></div>
                    <h2 className="text-lg font-bold text-white">Internet Speed</h2>
                </div>
                <button onClick={onRunSpeedTest} disabled={isSpeedTestRunning}
                    aria-label={isSpeedTestRunning ? "Running speed test" : "Run speed test"}
                    title={isSpeedTestRunning ? "Running speed test" : "Run speed test"}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-400 ${isSpeedTestRunning ? 'bg-violet-500/10 text-violet-400' : 'bg-violet-600 hover:bg-violet-500 text-white'}`}>
                    {isSpeedTestRunning ? <><Loader2 className="w-3.5 h-3.5 animate-spin" aria-hidden="true" />Running...</> : <><Play className="w-3.5 h-3.5 fill-current" aria-hidden="true" />Run</>}
                </button>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                    <div className="text-xs text-slate-400 mb-1 flex items-center gap-1"><ArrowDown className="w-3 h-3" />Download</div>
                    <div className="text-xl font-mono font-bold text-white">{download} <span className="text-xs text-slate-500">Mbps</span></div>
                </div>
                <div>
                    <div className="text-xs text-slate-400 mb-1 flex items-center gap-1"><ArrowUp className="w-3 h-3" />Upload</div>
                    <div className="text-xl font-mono font-bold text-white">{upload} <span className="text-xs text-slate-500">Mbps</span></div>
                </div>
            </div>
            <div className="flex items-center justify-between text-sm border-t border-slate-700/50 pt-3">
                <span className="text-slate-400">Ping: <span className="text-white font-mono">{ping}ms</span></span>
                <span className="text-xs text-slate-500">{timeAgo}</span>
            </div>
        </div>
    );
};

export default React.memo(SpeedTestCard);
