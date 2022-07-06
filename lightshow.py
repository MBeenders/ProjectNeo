import spotify
import json
import serial


class Show:
    def __init__(self):
        self.current_time = 0  # milliseconds
        self.current_track = ""  # name of track

        # Initialize spotify
        self.spotify = spotify.SpotifyPlayer()

        # Initialize arduino
        # TODO: convert to Bluetooth
        self.arduino = serial.Serial(port='COM8', baudrate=38400, timeout=.1)

    def sync_with_spotify(self):
        self.spotify.update()
        self.current_time = self.spotify.current_track_progress
        self.current_track = self.spotify.current_track_name

    def write_to_arduino(self, data):
        # TODO: convert to commands
        self.arduino.write(bytes(f'{data} ', 'utf-8'))
