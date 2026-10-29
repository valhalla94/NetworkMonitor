💡 **What:**
Added `if (document.hidden)` checks inside background polling intervals (for hosts, network status, public IP history, speed test history, and metrics) in `Dashboard.jsx` and `StatusPage.jsx` to prevent data fetching when the browser tab is inactive. Added a `visibilitychange` event listener to catch up on skipped data fetches based on elapsed time (`lastFetchTime`) since the last fetch. Added a check inside the interval callback to prevent double fetches.

🎯 **Why:**
The application continuously polls for data even when the user is not actively viewing the tab. This wastes client battery and CPU, and increases unnecessary load on the backend server.

📊 **Impact:**
Significantly reduces background network requests, CPU usage, and battery consumption on the client, as well as load on the backend server, especially for users who leave the dashboard open in a background tab for extended periods.

🔬 **Measurement:**
1. Open the dashboard in a browser tab.
2. Open network tools to observe polling requests.
3. Switch to another tab or minimize the browser for > 1 minute.
4. Observe that no new requests are made in the background.
5. Return to the dashboard tab and observe immediate "catch-up" requests fetching the latest data.
