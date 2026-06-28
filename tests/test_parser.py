from foggui.parser import parse_packet

def test_packets():
    result = parse_packet("905302,7/4/25,20:11:1,235.06,53,1000.44,34.20,22.40,35.30,7,36.9898683,-122.0525483,1.14,171.7,0.036,9999,25.36,32.86,26.25,32.28,83271,28.60,83307,27.88")
    assert result.altitude_m == 171.7
    assert result.pressure_mb == 1000.44
    assert result.humidity_pct == 22.40
    assert result.uptime_s == 235.06
    assert result.raw_line == "905302,7/4/25,20:11:1,235.06,53,1000.44,34.20,22.40,35.30,7,36.9898683,-122.0525483,1.14,171.7,0.036,9999,25.36,32.86,26.25,32.28,83271,28.60,83307,27.88"

def test_rejects_short_packet():
    assert parse_packet("905302,7/4/25,20:11:1") is None

def test_rejects_wrong_prefix():
    assert parse_packet("000000,7/4/25,20:11:1,235.06,53,1000.44,34.20,22.40,35.30,7,36.9898683,-122.0525483,1.14,171.7,0.036,9999,25.36,32.86,26.25,32.28,83271,28.60,83307,27.88") is None

def test_rejects_bad_value():
    assert parse_packet("905302,7/4/25,20:11:1,235.06,53,ERR,34.20,22.40,35.30,7,36.9898683,-122.0525483,1.14,171.7,0.036,9999,25.36,32.86,26.25,32.28,83271,28.60,83307,27.88") is None

def test_rejects_empty():
    assert parse_packet("") is None