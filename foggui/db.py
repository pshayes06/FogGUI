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
        cur.execute("UPDATE flights SET ended_at = NOW() WHERE id = %s", flight_id)
    conn.commit()