import React from 'react';
import { Globe, Clock, AlertTriangle } from 'lucide-react';

const setField = (setter) => (e) => setter(prev => ({ ...prev, [e.target.name]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }));

const HostFormFields = ({ f, setF, compact = false }) => (
    <div className={`space-y-4 ${compact ? 'text-sm' : ''}`}>
        <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2 space-y-1">
                <label className="text-xs font-medium text-slate-400">Host Name *</label>
                <div className="relative">
                    <Globe className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                    <input name="name" type="text" placeholder="e.g. Google DNS" value={f.name}
                        onChange={setField(setF)} required
                        className="glass-input w-full pl-9 pr-3 py-2 rounded-lg outline-none text-sm" />
                </div>
            </div>
            <div className="col-span-2 space-y-1">
                <label className="text-xs font-medium text-slate-400">IP / Hostname *</label>
                <input name="ip_address" type="text" placeholder="8.8.8.8" value={f.ip_address}
                    onChange={setField(setF)} required
                    className="glass-input w-full px-3 py-2 rounded-lg outline-none text-sm font-mono" />
            </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
                <label className="text-xs font-medium text-slate-400">Monitor Type</label>
                <select name="monitor_type" value={f.monitor_type} onChange={setField(setF)}
                    className="glass-input w-full px-3 py-2 rounded-lg outline-none bg-slate-800/50 text-sm">
                    <option value="icmp">ICMP Ping</option>
                    <option value="tcp">TCP Port</option>
                    <option value="http">HTTP/HTTPS</option>
                    <option value="heartbeat">Heartbeat</option>
                </select>
            </div>
            <div className="space-y-1">
                <label className="text-xs font-medium text-slate-400">Group</label>
                <input name="group_name" type="text" placeholder="General" value={f.group_name}
                    onChange={setField(setF)}
                    className="glass-input w-full px-3 py-2 rounded-lg outline-none text-sm" />
            </div>
        </div>

        {(f.monitor_type === 'tcp') && (
            <div className="space-y-1">
                <label className="text-xs font-medium text-slate-400">Port *</label>
                <input name="port" type="number" placeholder="80" value={f.port}
                    onChange={setField(setF)} required
                    className="glass-input w-full px-3 py-2 rounded-lg outline-none text-sm" />
            </div>
        )}

        {(f.monitor_type === 'http') && (
            <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                    <label className="text-xs font-medium text-slate-400">Expected Status</label>
                    <input name="expected_status_code" type="number" placeholder="200" value={f.expected_status_code}
                        onChange={setField(setF)}
                        className="glass-input w-full px-3 py-2 rounded-lg outline-none text-sm" />
                </div>
                <div className="flex items-end pb-2">
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input name="ssl_monitor" type="checkbox" checked={f.ssl_monitor} onChange={setField(setF)}
                            className="w-4 h-4 rounded border-slate-600 bg-slate-700" />
                        <span className="text-xs text-slate-300">Monitor SSL</span>
                    </label>
                </div>
            </div>
        )}

        {f.monitor_type === 'heartbeat' && (
            <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                    <label className="text-xs font-medium text-slate-400">Heartbeat Slug *</label>
                    <input name="heartbeat_slug" type="text" placeholder="my-service" value={f.heartbeat_slug}
                        onChange={setField(setF)}
                        className="glass-input w-full px-3 py-2 rounded-lg outline-none text-sm font-mono" />
                </div>
                <div className="space-y-1">
                    <label className="text-xs font-medium text-slate-400">Expected Every (s)</label>
                    <input name="heartbeat_interval" type="number" placeholder="300" value={f.heartbeat_interval}
                        onChange={setField(setF)}
                        className="glass-input w-full px-3 py-2 rounded-lg outline-none text-sm" />
                </div>
            </div>
        )}

        <div className="grid grid-cols-2 gap-3">
            {f.monitor_type !== 'heartbeat' && (
                <div className="space-y-1">
                    <label className="text-xs font-medium text-slate-400">
                        <Clock className="inline w-3 h-3 mr-1" />
                        Interval (s)
                    </label>
                    <input name="interval" type="number" placeholder="30" value={f.interval}
                        onChange={setField(setF)} min="5"
                        className="glass-input w-full px-3 py-2 rounded-lg outline-none text-sm" />
                </div>
            )}
            <div className="space-y-1">
                <label className="text-xs font-medium text-slate-400">
                    <AlertTriangle className="inline w-3 h-3 mr-1" />
                    Latency Alert (ms)
                </label>
                <input name="latency_threshold_ms" type="number" placeholder="Optional" value={f.latency_threshold_ms}
                    onChange={setField(setF)}
                    className="glass-input w-full px-3 py-2 rounded-lg outline-none text-sm" />
            </div>
        </div>

        <div className="space-y-2 pt-1 border-t border-slate-700/50">
            <label className="text-xs font-medium text-slate-400">Scheduled Maintenance Window</label>
            <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                    <label className="text-xs text-slate-500">From</label>
                    <input name="maintenance_start" type="datetime-local" value={f.maintenance_start}
                        onChange={setField(setF)}
                        className="glass-input w-full px-3 py-2 rounded-lg outline-none text-sm" />
                </div>
                <div className="space-y-1">
                    <label className="text-xs text-slate-500">To</label>
                    <input name="maintenance_end" type="datetime-local" value={f.maintenance_end}
                        onChange={setField(setF)}
                        className="glass-input w-full px-3 py-2 rounded-lg outline-none text-sm" />
                </div>
            </div>
        </div>

        <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
                <input name="maintenance" type="checkbox" checked={f.maintenance} onChange={setField(setF)}
                    className="w-4 h-4 rounded border-slate-600 bg-slate-700" />
                <span className="text-xs text-slate-300">Maintenance Mode</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
                <input name="enabled" type="checkbox" checked={f.enabled} onChange={setField(setF)}
                    className="w-4 h-4 rounded border-slate-600 bg-slate-700" />
                <span className="text-xs text-slate-300">Enabled</span>
            </label>
        </div>
    </div>
);

export default HostFormFields;
