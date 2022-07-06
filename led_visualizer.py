import pyaudio
import spotipy
import time
import numpy as np
import bluetooth
from scipy.fft import fft
import time


class SWHear(object):
    """
    The SWHear class is made to provide access to continuously recorded
    (and mathematically processed) microphone data.
    """

    def __init__(self, device=None, start_streaming=True):
        """fire up the SWHear class."""
        print(" -- initializing SWHear")

        self.chunk = 2000  # number of data points to read at a time
        self.rate = 50000  # time resolution of the recording device (Hz)

        # for tape recording (continuous "tape" of recent audio)
        self.tapeLength = 0.05  # seconds
        self.tape = np.empty(int(self.rate * self.tapeLength)) * np.nan

        self.p = pyaudio.PyAudio()  # start the PyAudio class
        self.prev_volume = 0

        # fourier
        self.cutoff = 500
        self.bars = 100
        self.bar_values = np.zeros(self.bars)

        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')

        for i in range(0, numdevices):
            if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", self.p.get_device_info_by_host_api_device_index(0, i).get('name'))

        if start_streaming:
            self.stream_start()

        self.bt = bluetooth.Bluetooth()

    ### LOWEST LEVEL AUDIO ACCESS
    # pure access to microphone and stream operations
    # keep math, plotting, FFT, etc out of here.

    def stream_read(self):
        """return values for a single chunk"""
        data = np.fromstring(self.stream.read(self.chunk), dtype=np.int16)
        # print(data)
        return data

    def stream_start(self):
        """connect to the audio device and start a stream"""
        print(" -- stream started")
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1,
                                  rate=self.rate, input=True,
                                  frames_per_buffer=self.chunk,
                                  input_device_index=4)

    def stream_stop(self):
        """close the stream but keep the PyAudio instance alive."""
        if 'stream' in locals():
            self.stream.stop_stream()
            self.stream.close()
        print(" -- stream CLOSED")

    def close(self):
        """gently detach from things."""
        self.stream_stop()
        self.p.terminate()

    ### TAPE METHODS
    # tape is like a circular magnetic ribbon of tape that's continuously
    # recorded and recorded over in a loop. self.tape contains this data.
    # the newest data is always at the end. Don't modify data on the type,
    # but rather do math on it (like FFT) as you read from it.

    def tape_add(self):
        """add a single chunk to the tape."""
        self.tape[:-self.chunk] = self.tape[self.chunk:]
        self.tape[-self.chunk:] = self.stream_read()

    def tape_flush(self):
        """completely fill tape with new data."""
        reads_in_tape = int(self.rate * self.tapeLength / self.chunk)
        print(" -- flushing %d s tape with %dx%.2f ms reads" % \
              (self.tapeLength, reads_in_tape, self.chunk / self.rate))
        for i in range(reads_in_tape):
            self.tape_add()

    def tape_forever(self, plot_sec=.0001):
        t1 = 0
        # os.system('mpg123' + './sounds/MarioKartRandomBox.mp3')
        while True:
            self.tape_add()
            if (time.time() - t1) > plot_sec:
                t1 = time.time()

                waveform = np.nan_to_num(self.tape)
                volume = np.linalg.norm(waveform)//400


                # self.bt.send_to_arduino(f"r")
                self.fourier_analysis()
                self.bt.send_to_arduino(f"R{int(self.bar_values[0] / 1000)}")
                # write_read(-10)

    def fourier_analysis(self):
        yf = np.nan_to_num(fft(self.tape))[0:self.cutoff]
        for bar in range(self.bars):
            step_size = self.cutoff // self.bars
            self.bar_values[bar] = np.absolute(np.average(yf[bar * step_size:(bar + 1) * step_size]))


if __name__ == "__main__":
    ear = SWHear()
    ear.tape_forever()
    ear.close()
    print("DONE")
