from foggui.db import start_flight, insert_reading, get_readings, get_flight, end_flight
from foggui.parser import Reading
from datetime import datetime

def test_start_flight():
    assert isinstance(start_flight(), int)

def test_insert_reading():

    flight_id = start_flight()
    mock_reading = Reading(
        altitude_m=200.0,
        pressure_mb=990.0,
        humidity_pct=50.0,
        temp_pressure_c=25.0,
        temp_humidity_c=24.0,
        uptime_s=100.0,
        recorded_at=datetime(2025, 7, 4, 12, 0, 0),
        raw_line="test"
    )

    insert_reading(flight_id, mock_reading)
    assert len(get_readings(flight_id)) == 1
    assert get_readings(flight_id)[0]['altitude_m'] == 200

def test_end_flight():
    flight_id = start_flight()
    assert get_flight(flight_id)["ended_at"] is None
    end_flight(flight_id)
    assert get_flight(flight_id)["ended_at"] is not None
