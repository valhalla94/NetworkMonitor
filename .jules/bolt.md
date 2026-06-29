## 2024-06-22 - Optimize Fetching Latest Ping Results
**Learning:** Found a major performance bottleneck where the application fetched all ping results for hosts within the last 5 minutes from the database and then manually filtered down to the latest ping per host in Python. This consumed unnecessary memory and database transfer payload.
**Action:** Always prefer pushing computations down to the database level. For querying the latest record per group with SQLAlchemy (especially when SQLite lacks DISTINCT ON), use a subquery combining func.max() and group_by, and join it back to the main table.

## 2024-07-26 - Optimize Uptime History Aggregation
**Learning:** Found another performance bottleneck when calculating daily uptime history. The application was fetching all ping results (up to 129k+ rows for 90 days) into memory and manually grouping by day in Python.
**Action:** Pushed grouping and aggregation down to the database using `func.strftime` for the day key, `func.count` for total pings, and `func.sum` with `case` for successful pings. This reduces the number of transferred rows to just 1 per day.

## 2024-08-01 - Optimize Fetching Metrics Data
**Learning:** Found a performance bottleneck when the application fetches large amounts of metrics data via the `/metrics/{host_id}` and `/export/metrics/{host_id}` endpoints. SQLAlchemy was querying for entire `PingResultDB` objects and passing them back to python for processing. By unpacking only the `timestamp` and `latency` fields from the query natively, performance in processing large metrics timelines improved significantly and dropped memory payload parsing.
**Action:** Always prefer selecting specific columns over full models when large numbers of records are fetched in SQLAlchemy to decrease database transfer overhead.

## 2024-11-20 - Memoize expensive host list filtering and grouping
**Learning:** Found a performance bottleneck where the `Dashboard.jsx` component would re-process the list of `hosts` (filtering, grouping, and sorting) on *every* single render loop. Because the component has a lot of state variables that are updated frequently (like metrics polling, chart loaders, and quick ping), the list was being iterated and re-grouped unnecessarily and taking up valuable render time on lower-end devices.
**Action:** Use React's `useMemo` hook to cache the result of expensive array operations. By depending on `[hosts, searchQuery, statusFilter]`, the list processing is skipped when irrelevant state is updated, saving CPU cycles.

## 2025-01-22 - Optimize Database Reads with Composite Index
**Learning:** Found a performance bottleneck where querying `PingResultDB` by `host_id` and filtering/ordering by `timestamp` was slow for large datasets because it lacked a composite index. Separate indices on `host_id` and `timestamp` exist, but SQLite usually uses only one index per query, falling back to a sequential scan for the other.
**Action:** Add a composite index on frequently paired query fields `(host_id, timestamp)` in SQLAlchemy using `Index('ix_name', 'col1', 'col2')` to significantly speed up range and exact-match queries that depend on both columns.

## 2025-02-12 - Remove Unused Queries in High-Frequency Paths
**Learning:** Found a major performance bottleneck where the `_get_sse_data` function executed an expensive subquery and join to fetch `latest_pings` every 5 seconds for every connected client, but the result was completely unused in the JSON payload sent to the client. This wasted significant database CPU and I/O.
**Action:** Always verify that the results of expensive queries, especially those within high-frequency execution paths like SSE loops or polling endpoints, are actually being used. Removing dead database queries is the easiest way to prevent overhead.
