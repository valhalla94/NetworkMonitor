import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import HostManager from '../components/HostManager';

// Mock API calls
vi.mock('../api', () => ({
    createHost: vi.fn().mockResolvedValue({ data: { id: 1, name: 'Test' } }),
    updateHost: vi.fn().mockResolvedValue({ data: {} }),
    deleteHost: vi.fn().mockResolvedValue({ data: {} }),
}));

describe('HostManager', () => {
    const mockHosts = [
        { id: 1, name: 'Test Host', ip_address: '192.168.1.1', interval: 30, monitor_type: 'icmp', enabled: true, group_name: 'General', maintenance: false, last_status: 'UP', ssl_monitor: false, ssl_expiry_days: null, latency_threshold_ms: null, average_latency: 12.3, port: null, heartbeat_slug: null, heartbeat_interval: null },
    ];

    it('renders managed hosts table', () => {
        render(<HostManager hosts={mockHosts} onHostAdded={() => {}} onHostDeleted={() => {}} />);
        expect(screen.getByText('Managed Hosts')).toBeInTheDocument();
        expect(screen.getByText('Test Host')).toBeInTheDocument();
    });

    it('shows Add Host panel on button click', () => {
        render(<HostManager hosts={[]} onHostAdded={() => {}} onHostDeleted={() => {}} />);
        fireEvent.click(screen.getByText('Add Host'));
        expect(screen.getByText('Add New Host')).toBeInTheDocument();
    });

    it('shows empty state when no hosts', () => {
        render(<HostManager hosts={[]} onHostAdded={() => {}} onHostDeleted={() => {}} />);
        expect(screen.getByText(/No hosts added yet/)).toBeInTheDocument();
    });

    it('shows edit controls on edit button click', () => {
        render(<HostManager hosts={mockHosts} onHostAdded={() => {}} onHostDeleted={() => {}} />);
        const editBtn = screen.getByTitle('Edit');
        fireEvent.click(editBtn);
        expect(screen.getByTitle('Save')).toBeInTheDocument();
        expect(screen.getByTitle('Cancel')).toBeInTheDocument();
    });
});
