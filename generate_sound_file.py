import math
import wave
import struct




#audio is a global variable containing a list of all samples
audio = []

# 44100 is the industry standard sample rate - CD quality.
sample_rate = 44100.0



def append_sinewave(
        freq=440.0, 
        duration_milliseconds=500, 
        volume=1.0):

    global audio

    num_samples = duration_milliseconds * (sample_rate / 1000.0)

    for x in range(int(num_samples)):
        audio.append(volume * math.sin(2 * math.pi * freq * ( x / sample_rate )))

    return


def save_wav(file_name):
    # Open up a wav file
    wav_file=wave.open(file_name,"w")

    # wav params
    nchannels = 1

    sampwidth = 2

    nframes = len(audio)
    comptype = "NONE"
    compname = "not compressed"
    wav_file.setparams((nchannels, sampwidth, sample_rate, nframes, comptype, compname))

    # WAV files here are using short, 16 bit, signed integers for the 
    # sample size.  So we multiply the floating point data we have by 32767, the
    # maximum value for a short integer.
    for sample in audio:
        wav_file.writeframes(struct.pack('h', int( sample * 32767.0 )))

    wav_file.close()

    return

for i in range(1,11):
    append_sinewave(freq=100*i)

    
save_wav("soundfile.wav")