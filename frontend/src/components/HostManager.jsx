import React, { useState } from 'react';
import { createHost, updateHost, deleteHost } from '../api';
import { Plus, Trash2, Globe, Clock, Edit2, X, Check } from 'lucide-react';

const HostManager = ({ onHostAdded, hosts, onHostDeleted }) => {
    const [name, setName] = useState('');
    const [ip, setIp] = useState('');
    const [interval, setInterval] = useState(30);
    const [editingHost, setEditingHost] = useState(null);
    const [editForm, setEditForm] = useState({ name: '', ip_address: '', interval: 30, enabled: true });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await createHost({ name, ip_address: ip, interval: parseInt(interval), enabled: true });
            setName('');
            setIp('');
            setInterval(30);
            if (onHostAdded) onHostAdded();
        } catch (error) {
            console.error("Error creating host:", error);
            alert("Failed to create host");
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this host?')) {
            try {
                await deleteHost(id);
                if (onHostDeleted) onHostDeleted();
            } catch (error) {
                console.error("Error deleting host:", error);
            }
        }
    };

    const startEdit = (host) => {
        setEditingHost(host.id);
        setEditForm({
            name: host.name,
            ip_address: host.ip_address,
            interval: host.interval,
            enabled: host.enabled
        });
    };

    const cancelEdit = () => {
        setEditingHost(null);
        setEditForm({ name: '', ip_address: '', interval: 30, enabled: true });
    };

    const saveEdit = async (hostId) => {
        try {
            await updateHost(hostId, editForm);
            setEditingHost(null);
            if (onHostAdded) onHostAdded();
        } catch (error) {
            console.error("Error updating host:", error);
            alert("Failed to update host");
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Add Host Form */}
            <div className="glass-panel p-8 rounded-2xl h-fit">
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-3 text-white">
                    <Plus className="text-blue-400" />
                    Add New Host
                </h2>
                <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300 ml-1">Host Name</label>
                        <div className="relative">
                            <Globe className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                            <input
                                type="text"
                                placeholder="e.g. Google DNS"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="glass-input w-full pl-10 pr-4 py-2.5 rounded-xl outline-none"
                                required
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300 ml-1">IP Address / Hostname</label>
                        <div className="relative">
                            <Globe className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                            <input
                                type="text"
                                placeholder="e.g. 8.8.8.8"
                                value={ip}
                                onChange={(e) => setIp(e.target.value)}
                                className="glass-input w-full pl-10 pr-4 py-2.5 rounded-xl outline-none"
                                required
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300 ml-1">Ping Interval (sec)</label>
                        <div className="relative">
                            <Clock className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                            <input
                                type="number"
                                placeholder="30"
                                value={interval}
                                onChange={(e) => setInterval(e.target.value)}
                                className="glass-input w-full pl-10 pr-4 py-2.5 rounded-xl outline-none"
                                min="5"
                                required
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="glass-button w-full py-3 rounded-xl font-bold text-lg mt-4 flex items-center justify-center gap-2"
                    >
                        <Plus className="w-5 h-5" />
                        Add Host
                    </button>
                </form>
            </div>

            {/* Host List */}
            <div className="lg:col-span-2 glass-panel p-8 rounded-2xl">
                <h2 className="text-2xl font-bold mb-6 text-white">Managed Hosts</h2>
                <div className="overflow-hidden rounded-xl border border-slate-700/50">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-slate-800/50 text-slate-300">
                                <th className="p-4 font-semibold">Name</th>
                                <th className="p-4 font-semibold">Address</th>
                                <th className="p-4 font-semibold">Interval</th>
                                <th className="p-4 font-semibold text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700/50">
                            {hosts.length === 0 ? (
                                <tr>
                                    <td colSpan="4" className="p-8 text-center text-slate-500">
                                        No hosts added yet. Add one to start monitoring.
                                    </td>
                                </tr>
                            ) : (
                                hosts.map((host) => (
                                    <tr key={host.id} className="hover:bg-slate-800/30 transition-colors">
                                        {editingHost === host.id ? (
                                            <>
                                                <td className="p-4">
                                                    <input
                                                        type="text"
                                                        value={editForm.name}
                                                        onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                                                        className="glass-input w-full px-3 py-1.5 rounded-lg outline-none text-sm"
                                                    />
                                                </td>
                                                <td className="p-4">
                                                    <input
                                                        type="text"
                                                        value={editForm.ip_address}
                                                        onChange={(e) => setEditForm({ ...editForm, ip_address: e.target.value })}
                                                        className="glass-input w-full px-3 py-1.5 rounded-lg outline-none text-sm font-mono"
                                                    />
                                                </td>
                                                <td className="p-4">
                                                    <input
                                                        type="number"
                                                        value={editForm.interval}
                                                        onChange={(e) => setEditForm({ ...editForm, interval: parseInt(e.target.value) })}
                                                        className="glass-input w-20 px-3 py-1.5 rounded-lg outline-none text-sm"
                                                        min="5"
                                                    />
                                                </td>
                                                <td className="p-4 text-right">
                                                    <div className="flex gap-2 justify-end">
                                                        <button
                                                            onClick={() => saveEdit(host.id)}
                                                            className="p-2 text-emerald-400 hover:bg-emerald-500/10 rounded-lg transition-colors"
                                                            title="Save Changes"
                                                        >
                                                            <Check className="w-5 h-5" />
                                                        </button>
                                                        <button
                                                            onClick={cancelEdit}
                                                            className="p-2 text-slate-400 hover:bg-slate-500/10 rounded-lg transition-colors"
                                                            title="Cancel"
                                                        >
                                                            <X className="w-5 h-5" />
                                                        </button>
                                                    </div>
                                                </td>
                                            </>
                                        ) : (
                                            <>
                                                <td className="p-4 font-medium text-white">{host.name}</td>
                                                <td className="p-4 text-slate-300 font-mono text-sm">{host.ip_address}</td>
                                                <td className="p-4 text-slate-300">{host.interval}s</td>
                                                <td className="p-4 text-right">
                                                    <div className="flex gap-2 justify-end">
                                                        <button
                                                            onClick={() => startEdit(host)}
                                                            className="p-2 text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors"
                                                            title="Edit Host"
                                                        >
                                                            <Edit2 className="w-5 h-5" />
                                                        </button>
                                                        <button
                                                            onClick={() => handleDelete(host.id)}
                                                            className="p-2 text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                                                            title="Delete Host"
                                                        >
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
