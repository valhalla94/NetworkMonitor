
def test_export_metrics_yields(client, auth_headers, db_session):
    from datetime import datetime, timedelta

    import models

    # Create host
    create_resp = client.post(
        "/hosts/",
        json={
            "name": "Host Export Test",
            "ip_address": "10.0.0.10",
            "interval": 30,
        },
        headers=auth_headers,
    )
    host_id = create_resp.json()["id"]

    now = datetime.utcnow()
    # Insert some PingResultDB records
    pings = []
    for i in range(2500):
        pings.append(
            models.PingResultDB(
                host_id=host_id, latency=float(i), timestamp=now - timedelta(seconds=i)
            )
        )
    db_session.add_all(pings)
    db_session.commit()

    # Request export
    response = client.get(f"/export/metrics/{host_id}?range=-1h", headers=auth_headers)
    assert response.status_code == 200

    lines = response.text.split("\n")
    assert len(lines) > 2500
