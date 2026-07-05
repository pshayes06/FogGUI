import psycopg2
import threading
from foggui.parser import Reading
from typing import Optional
import os

_local = threading.local()
_url = os.environ.get("DATABASE_URL")

def get_conn():
    if not hasattr(_local, 'conn') or _local.conn.closed:
        if _url:
            _local.conn = psycopg2.connect(_url)
        else:
            _local.conn = psycopg2.connect(database=os.environ.get("DB_NAME", "foggui"))
    return _local.conn

def start_flight(label: Optional[str] = None, started_at=None) -> int:
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            if started_at is not None:
                cur.execute("INSERT INTO flights (label, started_at) VALUES (%s, %s) RETURNING id", (label, started_at))
            else:
                cur.execute("INSERT INTO flights (label) VALUES (%s) RETURNING id", (label,))
            flight_id = cur.fetchone()[0]
    return flight_id

def insert_reading(flight_id: int, reading: Reading) -> None:
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO readings
                       (flight_id, recorded_at, uptime_s, altitude_m,
                        pressure_mb, temperature_c, humidity_pct, raw_line)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (flight_id, reading.recorded_at, reading.uptime_s, reading.altitude_m,
                 reading.pressure_mb, reading.temp_pressure_c, reading.humidity_pct, reading.raw_line),
            )

def end_flight(flight_id: int, ended_at=None) -> None:
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            if ended_at is not None:
                cur.execute("UPDATE flights SET ended_at = %s WHERE id = %s", (ended_at, flight_id))
            else:
                cur.execute("UPDATE flights SET ended_at = NOW() WHERE id = %s", (flight_id,))

def get_flight(flight_id: int) -> Optional[dict]:
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, started_at, ended_at, label FROM flights WHERE id = %s", (flight_id,))
            flight = cur.fetchone()
    if flight is None:
        return None
    return {"id": flight[0], "started_at": flight[1], "ended_at": flight[2], "label": flight[3]}

def get_flights() -> list:
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, started_at, ended_at, label FROM flights")
            flights = cur.fetchall()
    result = []
    for row in flights:
        result.append({"id": row[0], "started_at": row[1], "ended_at": row[2], "label": row[3]})
    return result

def get_readings(flight_id: int, min_alt: Optional[float] = None, max_alt: Optional[float] = None) -> list:
    query = "SELECT id, recorded_at, uptime_s, altitude_m, pressure_mb, temperature_c, humidity_pct FROM readings WHERE flight_id = %s"
    params = [flight_id]
    if min_alt is not None:
        query += " AND altitude_m >= %s"
        params.append(min_alt)
    if max_alt is not None:
        query += " AND altitude_m <= %s"
        params.append(max_alt)
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            readings = cur.fetchall()
    result = []
    for row in readings:
        result.append({
            "id": row[0], "recorded_at": row[1], "uptime_s": row[2],
            "altitude_m": row[3], "pressure_mb": row[4], "temperature_c": row[5], "humidity_pct": row[6],
        })
    return result

def update_flight_label(flight_id: int, label: str) -> None:
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE flights SET label = %s WHERE id = %s", (label, flight_id))

def delete_flight(flight_id: int) -> None:
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM flights WHERE id = %s", (flight_id,))
