from dataclasses import dataclass
from datetime import datetime
from typing import Optional

SERIAL = "905302"

@dataclass
class Reading:
    altitude_m: float
    pressure_mb: float
    humidity_pct: float
    temp_pressure_c: float
    temp_humidity_c: float
    recorded_at: datetime
    uptime_s: float
    raw_line: str

def parse_packet(line: str) -> Optional[Reading]:

    line = line.strip()
    fields = line.split(",")

    if len(fields) != 24 or fields[0] != SERIAL:
        return None
    
    try:
        recorded_at = datetime.strptime(f"{fields[1]} {fields[2]}", "%m/%d/%y %H:%M:%S")
        uptime_s = float(fields[3])
        pressure_mb = float(fields[5])
        temp_pressure = float(fields[6])
        humidity_pct = float(fields[7])
        temp_humidity = float(fields[8])
        altitude_m = float(fields[13])
    except ValueError:
        return None

    return Reading(
        altitude_m = altitude_m,
        pressure_mb = pressure_mb,
        humidity_pct = humidity_pct,
        temp_pressure_c = temp_pressure,
        temp_humidity_c = temp_humidity,
        recorded_at = recorded_at,
        uptime_s = uptime_s,
        raw_line = line,
    )