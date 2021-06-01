import unittest
import time
from qiskit_emulator import LocalUserMessenger, LocalUserMessengerClient

class LocalUserMessengerTest(unittest.TestCase):
    def test_local_user_messenger(self):
        messenger = LocalUserMessenger()
        messenger.listen()
        port = messenger.port()

        time.sleep(0.1)

        client = LocalUserMessengerClient(port)
        client.publish("something")
        # client.publish("something else")
        
        time.sleep(0.1)
        message_log = messenger.message_log()
        # self.assertEqual(2, len(message_log))
        self.assertEqual(1, len(message_log))
        self.assertEqual("something", message_log[0])
        # self.assertEqual(bytes("something else", 'utf-8'), message_log[1])


        

    
