import re

with open('backend/scheduler.py', 'r') as f:
    content = f.read()

content = re.sub(r'<<<<<<< HEAD\n.*?=======\n.*?\n>>>>>>> origin/main\n', r'''        hosts = (
            db.query(HostDB)
            .filter(
                HostDB.monitor_type == "heartbeat",
                HostDB.enabled == True,
                HostDB.heartbeat_interval != None,
            )
            .all()
        )

        if not hosts:
            return

        host_ids = [host.id for host in hosts]

        # Optimize: single query to get the latest ping timestamp for all heartbeat hosts
        latest_pings = (
            db.query(PingResultDB.host_id, func.max(PingResultDB.timestamp).label("max_ts"))
            .filter(PingResultDB.host_id.in_(host_ids))
            .group_by(PingResultDB.host_id)
            .all()
        )

        latest_ping_map = {row.host_id: row.max_ts for row in latest_pings}

        for host in hosts:
            cutoff = datetime.utcnow() - timedelta(seconds=host.heartbeat_interval * 2)
            last_timestamp = latest_ping_map.get(host.id)

            last = True if last_timestamp and last_timestamp >= cutoff else False
''', content, flags=re.DOTALL)

with open('backend/scheduler.py', 'w') as f:
    f.write(content)
