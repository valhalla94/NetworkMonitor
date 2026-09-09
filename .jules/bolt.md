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

## 2024-07-05 - Optimize state merges from high-frequency SSE updates
**Learning:** Found a performance bottleneck in `Dashboard.jsx` where the `hosts_update` SSE event merged incoming updates into the React state array using `.map()` combined with `.find()`. This resulted in an O(n^2) operation on the main UI thread during every update event (which occurs frequently), causing blocking and lag on lower-end devices with many hosts.
**Action:** When merging arrays of updates into existing React state arrays, construct an O(1) `Map` or dictionary for lookups first. Iterating through the state array and retrieving the updated value via a Map `get()` operation reduces the time complexity from O(n^2) to O(n), preventing UI thread starvation.

## 2025-02-09 - Remove Unused Database Queries in High-Frequency Loops
**Learning:** Found a performance bottleneck where an expensive subquery (fetching the latest ping per host) was being executed every 5 seconds inside the `_get_sse_data()` helper, but the resulting data (`latest_pings`) was completely unused when constructing the Server-Sent Events (SSE) payload.
**Action:** Always verify if fetched data is actually consumed by the application logic, especially inside high-frequency execution paths like SSE generators or polling loops. Removing dead queries saves considerable CPU and database I/O resources.

## 2024-02-14 - Optimize Fetching Global Network Status
**Learning:** Found a performance bottleneck where the application queried and joined the large `PingResultDB` table just to calculate `reachable_hosts`, `total_hosts`, and `global_avg_latency` on the high-traffic `/status` endpoint. Since `last_status` and `average_latency` are already pre-calculated and cached on the `HostDB` by the background scheduler, querying `PingResultDB` directly was redundant.
**Action:** Always verify if needed computed values are already cached on the parent model before performing expensive aggregations on time-series tables. Fetching only specific columns from `HostDB` reduces latency and database read time significantly.

## 2024-12-05 - Optimize fetching data for high-frequency SSE payload
**Learning:** Found a performance bottleneck where the `_get_sse_data` function fetched the entire `HostDB` ORM models on every single call (which happens every 5 seconds for each connected client), just to extract a subset of fields. SQLAlchemy ORM instantiation overhead is significant in high-frequency loops.
**Action:** When a high-frequency polling endpoint or SSE generator only needs specific fields, use SQLAlchemy's `db.query(Model.col1, Model.col2)` instead of `db.query(Model)`. This returns lightweight tuples directly instead of instantiating heavy ORM objects, significantly reducing memory allocation, GC pressure, and CPU overhead.
## 2025-02-12 - Prevent O(N) DOM Re-renders in Lists
**Learning:** Found a performance bottleneck in `HostManager.jsx` where the entire list of `hosts` was being re-rendered whenever a user typed into an edit form for a single row. This was because the `.map()` loop was rendering inline elements that were tightly coupled to the parent's `editForm` state, meaning every keystroke caused the parent and all children to re-render.
**Action:** Extract list items into a separate component wrapped with `React.memo()`. Crucially, ensure that dynamically changing state props (like `editForm`) are only passed to the specific item being edited (`isEditing ? editForm : null`) and use `useCallback` for event handlers so that non-editing items maintain stable prop references and skip re-renders.

## 2025-02-12 - Reduce SQLAlchemy ORM Instantiation Overhead
**Learning:** Found a performance optimization in the `/status` endpoint where fetching specific columns instead of full ORM models reduces the memory footprint and CPU overhead associated with SQLAlchemy model instantiation, particularly beneficial for high-traffic read-only endpoints.
**Action:** When querying for data where only a subset of columns is needed (especially for aggregation or simple JSON responses), use `db.query(Model.col1, Model.col2)` instead of `db.query(Model)` to bypass ORM object creation.

## 2025-02-12 - Optimize Date Formatting in Large Arrays
**Learning:** Found a major performance bottleneck where `new Date(d.time).toLocaleString()` was called inside a map loop iterating over thousands of metrics points. `Date.prototype.toLocaleString()` allocates new formatting objects on every call, leading to significant CPU blocking and lag on the main UI thread during parsing.
**Action:** Always extract the date formatting logic outside the map loop when parsing large time-series data sets. Instantiate a single `new Intl.DateTimeFormat()` before the loop and reuse it using `.format(new Date(...))` to speed up string generation by an order of magnitude.

## 2025-02-12 - Combine SQLite Transactions in High-Frequency Loops
**Learning:** Found a performance bottleneck where the `ping_host` function in the background scheduler opened a database session and committed a transaction to insert a ping result, and then immediately opened another session and transaction to update the host's status. Since SQLite locks the entire database for writes, multiple rapid consecutive transactions increase lock contention and overhead in high-frequency background loops (like the scheduler polling every few seconds).
**Action:** Always combine sequential insertions and updates into a single SQLAlchemy session and a single `db.commit()` block. This dramatically minimizes SQLite lock contention and database transaction overhead.

## 2025-02-12 - Stream Large CSV Exports
**Learning:** Found a major performance bottleneck where the application fetched up to a year's worth of metrics data using `.all()` and built an entire CSV string in memory via `io.StringIO()` for the `/export/metrics/{host_id}` endpoint. This caused massive memory spikes (e.g. 30MB+ for 100k rows) during exports.
**Action:** Always use SQLAlchemy's `.yield_per(1000)` combined with a Python generator to stream large datasets in chunks to the HTTP client (using FastAPI's `StreamingResponse`). This significantly drops peak memory footprint (e.g. down to <1MB) and prevents OOM crashes on high-load endpoints.
