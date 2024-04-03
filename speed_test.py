import wave
import sys
from pydub import AudioSegment
#sound = AudioSegment.from_file("deviprasadgharpehai.mp3")
sound = AudioSegment.from_mp3("output\\Audiofiles\\testGoogle.mp3")
sound.export("tester\\file.wav", format="wav")

# print(sys.argv[1])

import soundfile as sf
import pyrubberband as pyrb
y, sr = sf.read("tester\\file.wav")
# Play back at extra low speed
y_stretch = pyrb.time_stretch(y, sr, 0.5)
# Play back extra low tones
y_shift = pyrb.pitch_shift(y, sr, 0.5)
sf.write("tester\\analyzed_filepathX5.wav", y_stretch, sr, format='wav')

sound = AudioSegment.from_wav("tester\\analyzed_filepathX5.wav")
sound.export("tester\\analyzed_filepathX5.mp3", format="mp3")

# Play back at low speed
y_stretch = pyrb.time_stretch(y, sr, 0.75)
# Play back at low tones
y_shift = pyrb.pitch_shift(y, sr, 0.75)
sf.write("tester\\analyzed_filepathX75.wav", y_stretch, sr, format='wav')

sound = AudioSegment.from_wav("tester\\analyzed_filepathX75.wav")
sound.export("tester\\analyzed_filepathX75.mp3", format="mp3")

# Play back at 1.5X speed
y_stretch = pyrb.time_stretch(y, sr, 1.5)
# Play back two 1.5x tones
y_shift = pyrb.pitch_shift(y, sr, 1.5)
sf.write("tester\\analyzed_filepathX105.wav", y_stretch, sr, format='wav')

sound = AudioSegment.from_wav("tester\\analyzed_filepathX105.wav")
sound.export("tester\\analyzed_filepathX105.mp3", format="mp3")

# Play back at same speed
y_stretch = pyrb.time_stretch(y, sr, 1)
# Play back two smae-tones
y_shift = pyrb.pitch_shift(y, sr, 1)
sf.write("tester\\analyzed_filepathXnormal.wav", y_stretch, sr, format='wav')

sound = AudioSegment.from_wav("tester\\analyzed_filepathXnormal.wav")
sound.export("tester\\analyzed_filepathXnormal.mp3", format="mp3")