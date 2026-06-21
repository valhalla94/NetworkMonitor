import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import MockAdapter from 'axios-mock-adapter';
import api, {
    login,
    getHosts,
    createHost,
    updateHost,
    deleteHost,
    getMetrics,
    getUptimeHistory,
    getNetworkStatus,
    getPublicIpHistory,
    getSpeedTestHistory,
    runSpeedTest,
    quickPing,
    getSettings,
    updateNotificationSettings,
    getAuditLog
} from './api';

describe('API wrappers', () => {
    let mock;

    beforeEach(() => {
        mock = new MockAdapter(api);
    });

    afterEach(() => {
        mock.reset();
    });

    it('getHosts sends GET /hosts/', async () => {
        const mockData = [{ id: 1, name: 'Host 1' }];
        mock.onGet('/hosts/').reply(200, mockData);

        const response = await getHosts();

        expect(mock.history.get.length).toBe(1);
        expect(mock.history.get[0].url).toBe('/hosts/');
        expect(response.data).toEqual(mockData);
    });

    it('createHost sends POST /hosts/ with correct data', async () => {
        const payload = { name: 'New Host', ip: '127.0.0.1' };
        const mockData = { id: 2, ...payload };
        mock.onPost('/hosts/').reply(201, mockData);

        const response = await createHost(payload);

        expect(mock.history.post.length).toBe(1);
        expect(mock.history.post[0].url).toBe('/hosts/');
        expect(JSON.parse(mock.history.post[0].data)).toEqual(payload);
        expect(response.data).toEqual(mockData);
    });

    it('updateHost sends PUT /hosts/:id with correct data', async () => {
        const id = 1;
        const payload = { name: 'Updated Host' };
        const mockData = { id, ...payload };
        mock.onPut(`/hosts/${id}`).reply(200, mockData);

        const response = await updateHost(id, payload);

        expect(mock.history.put.length).toBe(1);
        expect(mock.history.put[0].url).toBe(`/hosts/${id}`);
        expect(JSON.parse(mock.history.put[0].data)).toEqual(payload);
        expect(response.data).toEqual(mockData);
    });

    it('deleteHost sends DELETE /hosts/:id', async () => {
        const id = 1;
        mock.onDelete(`/hosts/${id}`).reply(204);

        const response = await deleteHost(id);

        expect(mock.history.delete.length).toBe(1);
        expect(mock.history.delete[0].url).toBe(`/hosts/${id}`);
        expect(response.status).toBe(204);
    });

    it('getMetrics sends GET /metrics/:hostId with default range', async () => {
        const hostId = 1;
        mock.onGet(`/metrics/${hostId}`).reply(200, []);

        await getMetrics(hostId);

        expect(mock.history.get.length).toBe(1);
        expect(mock.history.get[0].url).toBe(`/metrics/${hostId}`);
        expect(mock.history.get[0].params).toEqual({ range: '-1h' });
    });

    it('getMetrics sends GET /metrics/:hostId with provided range', async () => {
        const hostId = 1;
        const range = '-24h';
        mock.onGet(`/metrics/${hostId}`).reply(200, []);

        await getMetrics(hostId, range);

        expect(mock.history.get.length).toBe(1);
        expect(mock.history.get[0].url).toBe(`/metrics/${hostId}`);
        expect(mock.history.get[0].params).toEqual({ range });
    });

    it('getUptimeHistory sends GET /uptime/:hostId with default range', async () => {
        const hostId = 1;
        mock.onGet(`/uptime/${hostId}`).reply(200, []);

        await getUptimeHistory(hostId);

        expect(mock.history.get.length).toBe(1);
        expect(mock.history.get[0].url).toBe(`/uptime/${hostId}`);
        expect(mock.history.get[0].params).toEqual({ range: '-30d' });
    });

    it('getUptimeHistory sends GET /uptime/:hostId with provided range', async () => {
        const hostId = 1;
        const range = '-7d';
        mock.onGet(`/uptime/${hostId}`).reply(200, []);

        await getUptimeHistory(hostId, range);

        expect(mock.history.get.length).toBe(1);
        expect(mock.history.get[0].url).toBe(`/uptime/${hostId}`);
        expect(mock.history.get[0].params).toEqual({ range });
    });

    it('getNetworkStatus sends GET /status', async () => {
        mock.onGet('/status').reply(200, {});

        await getNetworkStatus();

        expect(mock.history.get.length).toBe(1);
        expect(mock.history.get[0].url).toBe('/status');
    });

    it('getPublicIpHistory sends GET /public-ip-history', async () => {
        mock.onGet('/public-ip-history').reply(200, []);

        await getPublicIpHistory();

        expect(mock.history.get.length).toBe(1);
        expect(mock.history.get[0].url).toBe('/public-ip-history');
    });

    it('getSpeedTestHistory sends GET /speedtest/history', async () => {
        mock.onGet('/speedtest/history').reply(200, []);

        await getSpeedTestHistory();

        expect(mock.history.get.length).toBe(1);
        expect(mock.history.get[0].url).toBe('/speedtest/history');
    });

    it('runSpeedTest sends POST /speedtest/run', async () => {
        mock.onPost('/speedtest/run').reply(200, {});

        await runSpeedTest();

        expect(mock.history.post.length).toBe(1);
        expect(mock.history.post[0].url).toBe('/speedtest/run');
    });

    it('quickPing sends POST /tools/ping with target', async () => {
        const target = '8.8.8.8';
        mock.onPost('/tools/ping').reply(200, {});

        await quickPing(target);

        expect(mock.history.post.length).toBe(1);
        expect(mock.history.post[0].url).toBe('/tools/ping');
        expect(JSON.parse(mock.history.post[0].data)).toEqual({ target });
    });

    it('getSettings sends GET /settings', async () => {
        mock.onGet('/settings').reply(200, {});

        await getSettings();

        expect(mock.history.get.length).toBe(1);
        expect(mock.history.get[0].url).toBe('/settings');
    });

    it('updateNotificationSettings sends POST /settings/notifications with key/value', async () => {
        const url = 'http://webhook.example.com';
        mock.onPost('/settings/notifications').reply(200, {});

        await updateNotificationSettings(url);

        expect(mock.history.post.length).toBe(1);
        expect(mock.history.post[0].url).toBe('/settings/notifications');
        expect(JSON.parse(mock.history.post[0].data)).toEqual({ key: 'notification_url', value: url });
    });

    it('getAuditLog sends GET /audit-log with default limit', async () => {
        mock.onGet('/audit-log').reply(200, []);

        await getAuditLog();

        expect(mock.history.get.length).toBe(1);
        expect(mock.history.get[0].url).toBe('/audit-log');
        expect(mock.history.get[0].params).toEqual({ limit: 100 });
    });

    it('getAuditLog sends GET /audit-log with provided limit', async () => {
        const limit = 50;
        mock.onGet('/audit-log').reply(200, []);

        await getAuditLog(limit);

        expect(mock.history.get.length).toBe(1);
        expect(mock.history.get[0].url).toBe('/audit-log');
        expect(mock.history.get[0].params).toEqual({ limit });
    });

    it('login sends POST /token with FormData', async () => {
        mock.onPost('/token').reply(200, { access_token: '123' });

        const username = 'admin';
        const password = 'password123';
        await login(username, password);

        expect(mock.history.post.length).toBe(1);
        expect(mock.history.post[0].url).toBe('/token');
        const formData = mock.history.post[0].data;
        expect(formData instanceof FormData).toBe(true);
        expect(formData.get('username')).toBe(username);
        expect(formData.get('password')).toBe(password);
    });

});
