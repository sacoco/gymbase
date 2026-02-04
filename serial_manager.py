import serial
import threading
import time

class SerialManager:
    def __init__(self, port, baudrate, callback_code):
        self.port = port
        self.baudrate = baudrate
        self.callback_code = callback_code
        self.running = False
        self.thread = None
        self.serial_conn = None

    def start(self):
        if self.running or not self.port:
            return
        
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            self.thread = threading.Thread(target=self._listen, daemon=True)
            self.thread.start()
            return True
        except Exception as e:
            print(f"Error starting serial: {e}")
            return False

    def stop(self):
        self.running = False
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except:
                pass
            self.serial_conn = None

    def _listen(self):
        buffer = ""
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.is_open:
                    data = self.serial_conn.read().decode('utf-8', errors='ignore')
                    if data:
                        # Protocol: *1234#
                        if data == '*':
                            buffer = "" # Start new code
                        elif data == '#':
                            # End of code
                            if buffer:
                                self.callback_code(buffer)
                            buffer = ""
                        elif data.isdigit():
                            buffer += data
                        # Ignore other characters like newlines if any, unless protocol is stricter
                else:
                    time.sleep(0.5)
            except Exception as e:
                print(f"Serial Error: {e}")
                time.sleep(1)
