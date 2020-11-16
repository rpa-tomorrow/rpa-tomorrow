"""
Module for handling a continous stream of micrphone input
"""

import pyaudio
from six.moves import queue

# Audio recording configs
RATE = 16000  # optimal value for the google speech-to-text
CHUNK = int(RATE / 10)


class MicrophoneStream(object):
    def __init__(self, audio_interface):
        self.rate = RATE
        self.chunk = CHUNK
        self.buffer = queue.Queue()
        self.closed = True
        self.audio_interface = audio_interface

    def __enter__(self):
        self.audo_stream = self.audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,  # google api can only handle 1 channel audio
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
            stream_callback=self.buffer_push,
        )
        self.closed = False
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.audo_stream.stop_stream()
        self.audo_stream.close()
        self.closed = True
        self.buffer.put(None)  # stop signal
        self.audio_interface.terminate()

    # Unused arguments because it's required when used as PyAudio stream_callback
    def buffer_push(self, data, frame_count, time_info, status_flags):
        self.buffer.put(data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self.buffer.get()  # blocking get
            if chunk is None:
                return
            data = [chunk]

            # empty queue of chunks
            while True:
                try:
                    chunk = self.buffer.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break  # wait for more input

            yield b"".join(data)
