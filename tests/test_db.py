from foggui.db import start_flight, get_flight, end_flight

def test_start_flight():
    assert isinstance(start_flight(), int)

def test_end_flight():
    flight_id = start_flight()
    assert get_flight(flight_id)["ended_at"] is None
    end_flight(flight_id)
    assert get_flight(flight_id)["ended_at"] is not None