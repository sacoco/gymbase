import unittest
from unittest.mock import MagicMock, patch
import serial
from serial_manager import SerialManager

class TestSerialManager(unittest.TestCase):
    @patch('serial.Serial')
    def test_serial_connection(self, mock_serial):
        # Setup mock
        mock_instance = MagicMock()
        mock_serial.return_value = mock_instance
        mock_instance.is_open = True
        
        callback = MagicMock()
        mgr = SerialManager("COM_TEST", 9600, callback)
        
        # Test Start
        success = mgr.start()
        self.assertTrue(success)
        self.assertTrue(mgr.running)
        mock_serial.assert_called_with("COM_TEST", 9600, timeout=1)
        
        # Test Stop
        mgr.stop()
        self.assertFalse(mgr.running)
        mock_instance.close.assert_called()

    @patch('serial.Serial')
    def test_data_processing(self, mock_serial):
        # We need to simulate data being read
        # This is tricky because the thread runs in loop.
        # We can test the _listen logic by manually injecting data if we refactor,
        # or by mocking read to return specific sequence then raise exception to break loop (or just stop mgr).
        
        mock_instance = MagicMock()
        mock_serial.return_value = mock_instance
        mock_instance.is_open = True
        
        # Simulate: * 1 2 3 # then nothing
        # read() returns bytes or str depending on implementation but code assumes decode(), so bytes
        iterator = iter([b'*', b'1', b'2', b'3', b'#', b'', b''])
        mock_instance.read.side_effect = lambda: next(iterator)
        
        received_codes = []
        def callback(code):
            received_codes.append(code)
            
        mgr = SerialManager("COM_TEST", 9600, callback)
        
        # We don't want to start the thread because it blocks or races.
        # Let's verify logic by calling internal logic or running thread for short time.
        # Safest: Use thread but stop it quickly.
        
        mgr.start()
        import time
        time.sleep(0.1) 
        mgr.stop()
        
        # Check if code "123" was received
        # Note: Thread timing might be flaky. 
        # Ideally, we refactor `_listen` to be testable or accept an input stream.
        # But let's see if this works for basic integration.
        
        self.assertIn("123", received_codes)

if __name__ == '__main__':
    unittest.main()
