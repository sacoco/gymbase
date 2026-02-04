import serial
import threading
import time
import logging

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
            return False
        
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            self.thread = threading.Thread(target=self._listen, daemon=True)
            self.thread.start()
            logging.info(f"Serial connection started on {self.port} at {self.baudrate}")
            return True
        except Exception as e:
            logging.error(f"Error starting serial on {self.port}: {e}")
            return False

    def stop(self):
        if self.running:
            self.running = False
            logging.info("Stopping serial connection")
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
                                logging.debug(f"Serial code received: {buffer}")
                                self.callback_code(buffer)
                            buffer = ""
                        elif data.isdigit():
                            buffer += data
                        # Ignore other characters like newlines if any, unless protocol is stricter
                else:
                    time.sleep(0.5)
            except Exception as e:
                logging.error(f"Serial Error in listen loop: {e}")
                time.sleep(1)
