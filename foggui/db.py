import psycopg2
from foggui.parser import Reading

conn = psycopg2.connect(database="foggui")

def start_flight() -> int:
    with conn.cursor() as cur:
        cur.execute("INSERT INTO flights DEFAULT VALUES RETURNING id")
        flight_id = cur.fetchone()[0]
    conn.commit()
    return flight_id

def insert_reading(flight_id: int, reading: Reading) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO readings (flight_id, recorded_at, uptime_s, altitude_m, pressure_mb, temperature_c, humidity_pct, raw_line)" \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", \
            (flight_id, reading.recorded_at, reading.uptime_s, reading.altitude_m, reading.pressure_mb, reading.temp_pressure_c, reading.humidity_pct, reading.raw_line)
        )
    conn.commit()

def end_flight(flight_id: int) -> None:
    with conn.cursor() as cur:
        cur.execute("UPDATE flights SET ended_at = NOW() WHERE id = %s", (flight_id,))
    conn.commit()

def get_flights() -> list:
    with conn.cursor() as cur:
        cur.execute("SELECT id, started_at, ended_at, label FROM flights")
        flights = cur.fetchall()
    
    result = []
    for row in flights:
        result.append({
            "id": row[0],
            "started_at": row[1],
            "ended_at": row[2],
            "label": row[3]
        })
    
    return result

def get_readings(flight_id: int) -> list:
    with conn.cursor() as cur:
        cur.execute("SELECT id, recorded_at, uptime_s, altitude_m, pressure_mb, temperature_c, humidity_pct FROM readings " \
                    "WHERE flight_id = %s", (flight_id,))
        readings = cur.fetchall()
    
    result = []
    for row in readings:
        result.append({
            "id": row[0],
            "recorded_at": row[1],
            "uptime_s": row[2],
            "altitude_m": row[3],
            "pressure_mb": row[4],
            "temperature_c": row[5],
            "humidity_pct": row[6],
        })
    
    return result
        