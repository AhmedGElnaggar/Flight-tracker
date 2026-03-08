from flask import Flask, jsonify, render_template
from flask_cors import CORS
import requests
import pandas as pd
import time

app = Flask(__name__)
CORS(app)

OPENSKY_URL = "https://opensky-network.org/api/states/all"
AVIATIONSTACK_KEY = "7f7c992ad50d95ca8125d641ade6f981"

# Cache to avoid hitting OpenSky twice per page load
_cache = {'data': [], 'timestamp': 0, 'last_attempt': 0}
CACHE_TTL = 120  # 2 minutes between successful fetches
RETRY_WAIT = 300  # 5 minutes between failed attempts

def get_flights():
    global _cache
    now = time.time()

    # Return cached data if fresh
    if now - _cache['timestamp'] < CACHE_TTL and _cache['data']:
        return _cache['data']

    # Don't retry too soon after a failure
    if not _cache['data'] and now - _cache['last_attempt'] < RETRY_WAIT:
        print(f"Waiting before retry... {int(RETRY_WAIT - (now - _cache['last_attempt']))}s remaining")
        return []

    _cache['last_attempt'] = now
    try:
        res = requests.get(OPENSKY_URL, timeout=15)
        res.raise_for_status()
        data = res.json()
        flights = []
        for s in data.get("states", []):
            if s[5] and s[6] and s[1]:
                flights.append({
                    "callsign": s[1].strip(),
                    "origin_country": s[2],
                    "longitude": s[5],
                    "latitude": s[6],
                    "altitude": s[7] or 0,
                    "velocity": s[9] or 0,
                    "heading": s[10] or 0,
                    "on_ground": s[8]
                })
        _cache = {'data': flights, 'timestamp': now, 'last_attempt': now}
        print(f"Fetched {len(flights)} flights from OpenSky")
        return flights
    except Exception as e:
        print(f"OpenSky error: {e}")
        return _cache['data']

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/flights")
def flights():
    return jsonify(get_flights())

@app.route("/api/stats")
def stats():
    data = get_flights()
    if not data:
        return jsonify({})
    df = pd.DataFrame(data)
    airborne = df[df["on_ground"] == False]
    avg_altitude = round(airborne["altitude"].mean(), 2) if len(airborne) else 0
    avg_velocity = round(airborne["velocity"].mean(), 2) if len(airborne) else 0
    return jsonify({
        "total_flights": len(data),
        "airborne": len(airborne),
        "avg_altitude": avg_altitude,
        "avg_velocity": avg_velocity
    })

@app.route("/api/track/<flight_number>")
def track_flight(flight_number):
    try:
        res = requests.get(
            "http://api.aviationstack.com/v1/flights",
            params={
                "access_key": AVIATIONSTACK_KEY,
                "flight_iata": flight_number.upper(),
                "limit": 1
            },
            timeout=10
        )
        data = res.json()
        flights_data = data.get("data", [])
        if not flights_data:
            return jsonify({"valid": False, "error": "Flight not found"})
        f = flights_data[0]

        # Get status — normalize it
        raw_status = f.get("flight_status", "") or ""
        status_map = {
            "scheduled": "scheduled",
            "active": "active",
            "landed": "landed",
            "cancelled": "cancelled",
            "incident": "incident",
            "diverted": "diverted",
            "": "scheduled"
        }
        status = status_map.get(raw_status.lower(), raw_status.lower() or "scheduled")

        # Format times
        def fmt_time(iso):
            if not iso:
                return None
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
                return dt.strftime("%H:%M")
            except:
                return None

        dep = f.get("departure", {})
        arr = f.get("arrival", {})
        dep_time = fmt_time(dep.get("actual") or dep.get("estimated") or dep.get("scheduled"))
        arr_time = fmt_time(arr.get("estimated") or arr.get("scheduled"))

        return jsonify({
            "valid": True,
            "callsign": flight_number.upper(),
            "airline": f.get("airline", {}).get("name", "Unknown"),
            "status": status,
            "dep_iata": dep.get("iata", "???"),
            "dep_city": dep.get("airport", "Unknown"),
            "dep_time": dep_time,
            "arr_iata": arr.get("iata", "???"),
            "arr_city": arr.get("airport", "Unknown"),
            "arr_time": arr_time,
            "progress": calculate_progress(f)
        })
    except Exception as e:
        print(f"AviationStack error: {e}")
        return jsonify({"valid": False, "error": "Lookup failed"})

def calculate_progress(f):
    """Estimate flight progress based on departure/arrival times."""
    try:
        from datetime import datetime, timezone
        dep_actual = f.get("departure", {}).get("actual") or f.get("departure", {}).get("estimated")
        arr_estimated = f.get("arrival", {}).get("estimated") or f.get("arrival", {}).get("scheduled")
        if not dep_actual or not arr_estimated:
            status = f.get("flight_status", "")
            if status == "landed": return 100
            if status == "scheduled": return 0
            return 50
        dep_dt = datetime.fromisoformat(dep_actual.replace("Z", "+00:00"))
        arr_dt = datetime.fromisoformat(arr_estimated.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        total = (arr_dt - dep_dt).total_seconds()
        elapsed = (now - dep_dt).total_seconds()
        if total <= 0: return 50
        return max(2, min(98, int((elapsed / total) * 100)))
    except:
        return 50

if __name__ == "__main__":
    app.run(debug=True, port=5000)