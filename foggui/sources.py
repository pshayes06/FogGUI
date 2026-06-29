import serial, time
from serial.tools.list_ports import comports

BAUDRATE = 115200

class ReplaySource:
    def __init__(self, path: str, realtime: bool = False):
        self.path = path
        self.realtime = realtime

    def lines(self):
        with open(self.path) as f:
            for line in f:
                yield line
                if self.realtime:
                    time.sleep(0.5) # simulation purposes

class SerialSource:
    def lines(self):
        while True:
            ser = None
            for port in comports():
                try:
                    ser = serial.Serial(port.device, BAUDRATE, timeout=1)
                    break
                except serial.SerialException:
                    continue
            
            if ser is None:
                time.sleep(5)
                continue
                
            with ser:
                while True:
                    try:
                        line = ser.readline().decode("utf-8")
                        yield line
                    except serial.SerialException:
                        break