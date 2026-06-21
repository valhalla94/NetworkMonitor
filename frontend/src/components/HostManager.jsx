import React, { useState } from 'react';
import { createHost, updateHost, deleteHost } from '../api';
import { Plus, Trash2, Globe, Clock, Edit2, X, Check, AlertTriangle, Heart } from 'lucide-react';

const setField = (setter) => (e) => setter(prev => ({ ...prev, [e.target.name]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }));

const DEFAULT_FORM = {
    name: '',
    ip_address: '',
    port: '',
    interval: 30,
    enabled: true,
    monitor_type: 'icmp',
    ssl_monitor: false,
    expected_status_code: 200,
    group_name: 'General',
    maintenance: false,
    latency_threshold_ms: '',
    heartbeat_slug: '',
    heartbeat_interval: '',
    maintenance_start: '',
    maintenance_end: '',
};

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

const HostManager = ({ onHostAdded, hosts, onHostDeleted }) => {
    const [form, setForm] = useState(DEFAULT_FORM);
    const [editingHost, setEditingHost] = useState(null);
    const [editForm, setEditForm] = useState(DEFAULT_FORM);
    const [showAddPanel, setShowAddPanel] = useState(false);

    const buildPayload = (f) => ({
        name: f.name,
        ip_address: f.ip_address,
        port: f.port ? parseInt(f.port) : null,
        interval: parseInt(f.interval) || 30,
        enabled: f.enabled,
        monitor_type: f.monitor_type,
        ssl_monitor: f.ssl_monitor,
        expected_status_code: parseInt(f.expected_status_code) || 200,
        group_name: f.group_name || 'General',
        maintenance: f.maintenance,
        latency_threshold_ms: f.latency_threshold_ms ? parseFloat(f.latency_threshold_ms) : null,
        heartbeat_slug: f.heartbeat_slug || null,
        heartbeat_interval: f.heartbeat_interval ? parseInt(f.heartbeat_interval) : null,
        maintenance_start: f.maintenance_start || null,
        maintenance_end: f.maintenance_end || null,
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await createHost(buildPayload(form));
            setForm(DEFAULT_FORM);
            setShowAddPanel(false);
            onHostAdded?.();
        } catch (error) {
            console.error('Error creating host:', error);
            alert('Failed to create host');
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('Delete this host?')) {
            try {
                await deleteHost(id);
                onHostDeleted?.();
            } catch (error) {
                console.error('Error deleting host:', error);
            }
        }
    };

    const startEdit = (host) => {
        setEditingHost(host.id);
        setEditForm({
            name: host.name,
            ip_address: host.ip_address,
            port: host.port || '',
            interval: host.interval,
            enabled: host.enabled,
            monitor_type: host.monitor_type || 'icmp',
            ssl_monitor: host.ssl_monitor || false,
            expected_status_code: host.expected_status_code || 200,
            group_name: host.group_name || 'General',
            maintenance: host.maintenance || false,
            latency_threshold_ms: host.latency_threshold_ms || '',
            heartbeat_slug: host.heartbeat_slug || '',
            heartbeat_interval: host.heartbeat_interval || '',
            maintenance_start: host.maintenance_start ? host.maintenance_start.slice(0, 16) : '',
            maintenance_end: host.maintenance_end ? host.maintenance_end.slice(0, 16) : '',
        });
    };

    const saveEdit = async (hostId) => {
        try {
            await updateHost(hostId, buildPayload(editForm));
            setEditingHost(null);
            onHostAdded?.();
        } catch (error) {
            console.error('Error updating host:', error);
            alert('Failed to update host');
        }
    };

    return (
        <div className="space-y-6">
            {/* Header + Add Button */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">Managed Hosts</h2>
                <button
                    onClick={() => setShowAddPanel(true)}
                    className="glass-button px-5 py-2.5 rounded-xl font-medium flex items-center gap-2"
                >
                    <Plus className="w-5 h-5" />
                    Add Host
                </button>
            </div>

            {/* Slide-over Add Panel */}
            {showAddPanel && (
                <div className="fixed inset-0 z-50 flex justify-end">
                    <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setShowAddPanel(false)} />
                    <div className="relative w-full max-w-md bg-slate-900 border-l border-slate-700 h-full overflow-y-auto shadow-2xl animate-in slide-in-from-right duration-300">
                        <div className="p-6">
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                    <Plus className="text-blue-400 w-5 h-5" />
                                    Add New Host
                                </h3>
                                <button onClick={() => setShowAddPanel(false)} className="text-slate-400 hover:text-white transition-colors">
                                    <X className="w-6 h-6" />
                                </button>
                            </div>
                            <form onSubmit={handleSubmit} className="space-y-4">
                                <HostFormFields f={form} setF={setForm} />
                                <button type="submit" className="glass-button w-full py-3 rounded-xl font-bold flex items-center justify-center gap-2 mt-4">
                                    <Plus className="w-5 h-5" />
                                    Add Host
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            )}

            {/* Host Table */}
            <div className="glass-panel p-6 rounded-2xl">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-slate-800/50 text-slate-300">
                                <th className="p-4 font-semibold">Name</th>
                                <th className="p-4 font-semibold">Address</th>
                                <th className="p-4 font-semibold">Group</th>
                                <th className="p-4 font-semibold">Type</th>
                                <th className="p-4 font-semibold">Interval</th>
                                <th className="p-4 font-semibold text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700/50">
                            {hosts.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="p-8 text-center text-slate-500">
                                        No hosts added yet. Click "Add Host" to start monitoring.
                                    </td>
                                </tr>
                            ) : (
                                hosts.map((host) => (
                                    <tr key={host.id} className="hover:bg-slate-800/30 transition-colors">
                                        {editingHost === host.id ? (
                                            <>
                                                <td className="p-3" colSpan="4">
                                                    <HostFormFields f={editForm} setF={setEditForm} compact />
                                                </td>
                                                <td className="p-3" />
                                                <td className="p-3 text-right align-top">
                                                    <div className="flex gap-2 justify-end">
                                                        <button onClick={() => saveEdit(host.id)}
                                                            className="p-2 text-emerald-400 hover:bg-emerald-500/10 rounded-lg transition-colors" title="Save">
                                                            <Check className="w-5 h-5" />
                                                        </button>
                                                        <button onClick={() => setEditingHost(null)}
                                                            className="p-2 text-slate-400 hover:bg-slate-500/10 rounded-lg transition-colors" title="Cancel">
                                                            <X className="w-5 h-5" />
                                                        </button>
                                                    </div>
                                                </td>
                                            </>
                                        ) : (
                                            <>
                                                <td className="p-4 font-medium text-white">
                                                    {host.name}
                                                    {host.maintenance && (
                                                        <span className="ml-2 px-1.5 py-0.5 text-[10px] bg-amber-500/20 text-amber-400 rounded border border-amber-500/30">MAINT</span>
                                                    )}
                                                    {host.latency_threshold_ms && (
                                                        <span className="ml-2 px-1.5 py-0.5 text-[10px] bg-orange-500/10 text-orange-400 rounded border border-orange-500/20">
                                                            ⚡{host.latency_threshold_ms}ms
                                                        </span>
                                                    )}
                                                </td>
                                                <td className="p-4 text-slate-300 font-mono text-sm">{host.ip_address}</td>
                                                <td className="p-4 text-slate-300 text-sm">{host.group_name || '-'}</td>
                                                <td className="p-4 text-slate-300">
                                                    <span className={`px-2 py-1 rounded-md text-xs font-bold ${
                                                        host.monitor_type === 'http' ? 'bg-purple-500/20 text-purple-400' :
                                                        host.monitor_type === 'tcp' ? 'bg-orange-500/20 text-orange-400' :
                                                        host.monitor_type === 'heartbeat' ? 'bg-pink-500/20 text-pink-400' :
                                                        'bg-blue-500/20 text-blue-400'
                                                    }`}>
                                                        {host.monitor_type === 'tcp' ? `TCP:${host.port}` :
                                                         host.monitor_type === 'heartbeat' ? '💓 HB' :
                                                         host.monitor_type?.toUpperCase() || 'ICMP'}
                                                    </span>
                                                    {host.ssl_monitor && host.ssl_expiry_days !== null && (
                                                        <div className="mt-1">
                                                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                                                                host.ssl_expiry_days > 30 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                                                                host.ssl_expiry_days > 7 ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                                                                'bg-red-500/10 text-red-400 border-red-500/20'
                                                            }`}>
                                                                SSL: {host.ssl_expiry_days}d
                                                            </span>
                                                        </div>
                                                    )}
                                                </td>
                                                <td className="p-4 text-slate-300">
                                                    {host.monitor_type === 'heartbeat' ? `${host.heartbeat_interval || '?'}s` : `${host.interval}s`}
                                                </td>
                                                <td className="p-4 text-right">
                                                    <div className="flex gap-2 justify-end">
                                                        <button onClick={() => startEdit(host)}
                                                            className="p-2 text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors" title="Edit">
                                                            <Edit2 className="w-5 h-5" />
                                                        </button>
                                                        <button onClick={() => handleDelete(host.id)}
                                                            className="p-2 text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors" title="Delete">
                                                            <Trash2 className="w-5 h-5" />
                                                        </button>
                                                    </div>
                                                </td>
                                            </>
                                        )}
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default HostManager;
