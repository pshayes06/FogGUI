from app import app
from foggui.db import start_flight, get_flight

def test_get_flights():
    client = app.test_client()
    response = client.get("/api/flights")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_readings():

    client = app.test_client()
    response = client.get("/api/flights/1/readings")

    assert response.status_code == 200

def test_compare_flights():

    client = app.test_client()
    response = client.get("/api/flights/compare?ids=1,2")

    assert response.status_code == 200
    assert isinstance(response.get_json(), dict)

    response = client.get("/api/flights/compare")
    assert response.status_code == 400

def test_delete_flight():

    flight_id = start_flight()
    client = app.test_client()
    response = client.delete(f"/api/flights/{flight_id}")
    assert response.status_code == 204
    assert get_flight(flight_id) is None
    