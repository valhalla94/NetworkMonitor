## 2024-06-22 - Optimize Fetching Latest Ping Results
**Learning:** Found a major performance bottleneck where the application fetched all ping results for hosts within the last 5 minutes from the database and then manually filtered down to the latest ping per host in Python. This consumed unnecessary memory and database transfer payload.
**Action:** Always prefer pushing computations down to the database level. For querying the latest record per group with SQLAlchemy (especially when SQLite lacks DISTINCT ON), use a subquery combining func.max() and group_by, and join it back to the main table.

## 2024-07-26 - Optimize Uptime History Aggregation
**Learning:** Found another performance bottleneck when calculating daily uptime history. The application was fetching all ping results (up to 129k+ rows for 90 days) into memory and manually grouping by day in Python.
**Action:** Pushed grouping and aggregation down to the database using `func.strftime` for the day key, `func.count` for total pings, and `func.sum` with `case` for successful pings. This reduces the number of transferred rows to just 1 per day.
