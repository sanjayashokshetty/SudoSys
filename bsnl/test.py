from time import sleep

import pyaudio
import wave

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 128
RECORD_SECONDS = 10

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
speaker = audio.open(format=FORMAT, channels=CHANNELS,
                     rate=RATE, output=True,
                     frames_per_buffer=CHUNK)
print("recording...")
frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("finished recording")

for frame in frames:
    speaker.write(frame, CHUNK)


stream.stop_stream()
stream.close()
speaker.close()
audio.terminate()
