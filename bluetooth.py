import serial
import time


class Bluetooth:
    def __init__(self, port="COM7"):
        self.bluetooth = serial.Serial(port, 38400)  # Start communications with the bluetooth unit
        print("Connected to Bluetooth Device")
        self.bluetooth.flushInput()  # This gives the bluetooth a little kick

    def send_to_arduino(self, data, confirmation=True):
        self.bluetooth.write(data.encode('UTF-8'))  # These need to be bytes not unicode, plus a number

        if confirmation:
            self.receive_from_arduino()

    def receive_from_arduino(self):
        self.bluetooth.readline()  # This reads the incoming data

    def close_connection(self):
        self.bluetooth.close()  # Otherwise the connection will remain open until a timeout


# bt_connection = Bluetooth()
# start = time.time()
# for i in range(105):
#     bt_connection.send_to_arduino(f'V{i}')
#
# bt_connection.close_connection()
