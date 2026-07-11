const fs = require('fs');
let code = fs.readFileSync('frontend/src/components/HostFormFields.jsx', 'utf8');

code = code.replace("import React from 'react';", "import React, { useId } from 'react';");
code = code.replace("const HostFormFields = ({ f, setF, compact = false }) => (", "const HostFormFields = ({ f, setF, compact = false }) => {\n    const idPrefix = useId();\n    return (\n");
code = code.replace("    </div>\n);", "    </div>\n    );\n};");

// name
code = code.replace('<label className="text-xs font-medium text-slate-400">Host Name *</label>', '<label htmlFor={`${idPrefix}-name`} className="text-xs font-medium text-slate-400">Host Name *</label>');
code = code.replace('<input name="name" type="text"', '<input id={`${idPrefix}-name`} name="name" type="text"');

// ip_address
code = code.replace('<label className="text-xs font-medium text-slate-400">IP / Hostname *</label>', '<label htmlFor={`${idPrefix}-ip`} className="text-xs font-medium text-slate-400">IP / Hostname *</label>');
code = code.replace('<input name="ip_address" type="text"', '<input id={`${idPrefix}-ip`} name="ip_address" type="text"');

// monitor_type
code = code.replace('<label className="text-xs font-medium text-slate-400">Monitor Type</label>', '<label htmlFor={`${idPrefix}-monitor`} className="text-xs font-medium text-slate-400">Monitor Type</label>');
code = code.replace('<select name="monitor_type"', '<select id={`${idPrefix}-monitor`} name="monitor_type"');

// group_name
code = code.replace('<label className="text-xs font-medium text-slate-400">Group</label>', '<label htmlFor={`${idPrefix}-group`} className="text-xs font-medium text-slate-400">Group</label>');
code = code.replace('<input name="group_name" type="text"', '<input id={`${idPrefix}-group`} name="group_name" type="text"');

// port
code = code.replace('<label className="text-xs font-medium text-slate-400">Port *</label>', '<label htmlFor={`${idPrefix}-port`} className="text-xs font-medium text-slate-400">Port *</label>');
code = code.replace('<input name="port" type="number"', '<input id={`${idPrefix}-port`} name="port" type="number"');

// expected_status_code
code = code.replace('<label className="text-xs font-medium text-slate-400">Expected Status</label>', '<label htmlFor={`${idPrefix}-status`} className="text-xs font-medium text-slate-400">Expected Status</label>');
code = code.replace('<input name="expected_status_code" type="number"', '<input id={`${idPrefix}-status`} name="expected_status_code" type="number"');

// ssl_monitor
code = code.replace('<label className="flex items-center gap-2 cursor-pointer">\n                        <input name="ssl_monitor"', '<label htmlFor={`${idPrefix}-ssl`} className="flex items-center gap-2 cursor-pointer">\n                        <input id={`${idPrefix}-ssl`} name="ssl_monitor"');

// heartbeat_slug
code = code.replace('<label className="text-xs font-medium text-slate-400">Heartbeat Slug *</label>', '<label htmlFor={`${idPrefix}-hbslug`} className="text-xs font-medium text-slate-400">Heartbeat Slug *</label>');
code = code.replace('<input name="heartbeat_slug" type="text"', '<input id={`${idPrefix}-hbslug`} name="heartbeat_slug" type="text"');

// heartbeat_interval
code = code.replace('<label className="text-xs font-medium text-slate-400">Expected Every (s)</label>', '<label htmlFor={`${idPrefix}-hbinterval`} className="text-xs font-medium text-slate-400">Expected Every (s)</label>');
code = code.replace('<input name="heartbeat_interval" type="number"', '<input id={`${idPrefix}-hbinterval`} name="heartbeat_interval" type="number"');

// interval
code = code.replace('<label className="text-xs font-medium text-slate-400">\n                        <Clock className="inline w-3 h-3 mr-1" />\n                        Interval (s)\n                    </label>', '<label htmlFor={`${idPrefix}-interval`} className="text-xs font-medium text-slate-400">\n                        <Clock className="inline w-3 h-3 mr-1" />\n                        Interval (s)\n                    </label>');
code = code.replace('<input name="interval" type="number"', '<input id={`${idPrefix}-interval`} name="interval" type="number"');

// latency_threshold_ms
code = code.replace('<label className="text-xs font-medium text-slate-400">\n                    <AlertTriangle className="inline w-3 h-3 mr-1" />\n                    Latency Alert (ms)\n                </label>', '<label htmlFor={`${idPrefix}-latency`} className="text-xs font-medium text-slate-400">\n                    <AlertTriangle className="inline w-3 h-3 mr-1" />\n                    Latency Alert (ms)\n                </label>');
code = code.replace('<input name="latency_threshold_ms" type="number"', '<input id={`${idPrefix}-latency`} name="latency_threshold_ms" type="number"');

// maintenance_start
code = code.replace('<label className="text-xs text-slate-500">From</label>', '<label htmlFor={`${idPrefix}-mstart`} className="text-xs text-slate-500">From</label>');
code = code.replace('<input name="maintenance_start" type="datetime-local"', '<input id={`${idPrefix}-mstart`} name="maintenance_start" type="datetime-local"');

// maintenance_end
code = code.replace('<label className="text-xs text-slate-500">To</label>', '<label htmlFor={`${idPrefix}-mend`} className="text-xs text-slate-500">To</label>');
code = code.replace('<input name="maintenance_end" type="datetime-local"', '<input id={`${idPrefix}-mend`} name="maintenance_end" type="datetime-local"');

// maintenance mode
code = code.replace('<label className="flex items-center gap-2 cursor-pointer">\n                <input name="maintenance" type="checkbox"', '<label htmlFor={`${idPrefix}-maint`} className="flex items-center gap-2 cursor-pointer">\n                <input id={`${idPrefix}-maint`} name="maintenance" type="checkbox"');

// enabled
code = code.replace('<label className="flex items-center gap-2 cursor-pointer">\n                <input name="enabled" type="checkbox"', '<label htmlFor={`${idPrefix}-enabled`} className="flex items-center gap-2 cursor-pointer">\n                <input id={`${idPrefix}-enabled`} name="enabled" type="checkbox"');

fs.writeFileSync('frontend/src/components/HostFormFields.jsx', code);
console.log('done');
