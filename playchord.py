import pyaudio
import numpy as np

# Set up the audio stream
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=True)

# Set the frequencies of the notes in the C major chord
freqs = [261.63, 329.63, 392.0]

# Set the duration of the chord in seconds
duration = 2.0

# Set the volume of the chord (between 0 and 1)
volume = 0.5

# Generate the sine waves for each note in the chord
samples = []
for freq in freqs:
    sample = volume * np.sin(2*np.pi*np.arange(44100*duration)*freq/44100.0)
    samples.append(sample)

# Add the sine waves together to get the chord
chord = np.sum(samples, axis=0)

# Play the chord
stream.write(chord.astype(np.float32))

# Close the audio stream
stream.stop_stream()
stream.close()
p.terminate()