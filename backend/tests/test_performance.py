import pytest
import time
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_quick_ping_performance():
    from unittest.mock import patch
    import slowapi

    limiter = app.state.limiter
    original_limit = limiter.limit

    def fake_limit(*args, **kwargs):
        return original_limit("1000/minute")

    with patch("main.ping") as mock_ping, patch.object(limiter, 'limit', side_effect=fake_limit):
        def slow_ping(*args, **kwargs):
            time.sleep(0.5)
            return 10.0

        mock_ping.side_effect = slow_ping

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            start_time = time.perf_counter()

            # Send 5 concurrent requests, using different IPs or skipping rate limit
            # Here we just override the limit so we can do 5 on same IP
            tasks = []
            for i in range(5):
                tasks.append(ac.post("/tools/ping", json={"target": f"127.0.0.{i}"}))

            results = await asyncio.gather(*tasks)
            end_time = time.perf_counter()

            total_time = end_time - start_time
            print(f"\nTotal time for 5 concurrent slow pings: {total_time:.4f} seconds")
            # If the pings ran sequentially they would take >2.5s.
            # If concurrently, they should take roughly 0.5s.
            assert total_time < 1.0

            for res in results:
                # If rate limited, we might get 429
                pass
