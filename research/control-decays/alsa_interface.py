#!/usr/bin/env python

import pyaudio

import os
import numpy

import multiprocessing
import time

import sine
from defs_measure import RATE, ALSA_BUFFER_SIZE, PROCESS_BUFFER_SIZE
from defs_measure import FORMAT_ALSA, FORMAT_NUMPY, ALSA_BUFFER_SIZE_MULTIPLIER

DEVICE_NUMBER = 5 # TASCAM
#DEVICE_NUMBER = 0 # internal sound card

### portaudio should use plughw
os.environ['PA_ALSA_PLUGHW'] = '1'

def sinePlay(frequency_queue, stream_out):
    """ Plays a mono sine wave.  Send a float in frequency_queue
    to play that freq; send a 0 to pause output, or send a
    negative number to quit the function.  The phase of the sine
    wave is preserved during pausing."""
    sine_osc = sine.SineInt(440.0, RATE)
    sine_wave = numpy.empty( (ALSA_BUFFER_SIZE, 1), dtype=FORMAT_NUMPY )
    freq = 440.0
    while True:
        while not frequency_queue.empty():
            freq = frequency_queue.get()
            sine_osc.set_freq(freq)
        if freq == 0:
            time.sleep(0.1)
        elif freq < 0:
            break
        else:
            sine_osc.fill_buffer(sine_wave)
            sine_string = sine_wave.tostring()
            stream_out.write(sine_string)
def tascam_input(tascam_input_queue, alsa_stream_in):
    multiples = PROCESS_BUFFER_SIZE / ALSA_BUFFER_SIZE
    while True:
        left = numpy.empty(PROCESS_BUFFER_SIZE, dtype=FORMAT_NUMPY)
        right = numpy.empty(PROCESS_BUFFER_SIZE, dtype=FORMAT_NUMPY)
        for i in range(multiples):
            chunk = alsa_stream_in.read(ALSA_BUFFER_SIZE)
            data = numpy.fromstring(chunk, dtype=FORMAT_NUMPY)
            left[i*ALSA_BUFFER_SIZE:(i+1)*ALSA_BUFFER_SIZE] = data[0::2]
            right[i*ALSA_BUFFER_SIZE:(i+1)*ALSA_BUFFER_SIZE] = data[1::2]
        tascam_input_queue.put( (left, right) )


class Audio():
    def __init__(self):
        self.alsa_obj = pyaudio.PyAudio()

    def get_info(self):
        #print self.alsa_obj.get_default_host_api_info()
        alsa_info = self.alsa_obj.get_host_api_info_by_type(pyaudio.paALSA)
        alsa_index = alsa_info['index']
        for i in range(alsa_info['deviceCount']):
            alsa_device_info = self.alsa_obj.get_device_info_by_host_api_device_index(
                alsa_index, i)
            #print i, alsa_device_info['name']
            print i, alsa_device_info
        print '---'
        hosts = self.alsa_obj.get_host_api_count()
        for i in range(hosts):
            print i, self.alsa_obj.get_host_api_info_by_index(i)
        print pyaudio.paFloat32
        ok = self.alsa_obj.is_format_supported(
            RATE,
            input_device=DEVICE_NUMBER,
            input_channels=2,
            input_format=FORMAT_ALSA,
            output_device=DEVICE_NUMBER,
            output_channels=1,
            output_format=FORMAT_ALSA,
            )
        print ok
        #exit(0)


    def close(self):
        self.alsa_obj.terminate()
    

    def begin(self):
        # start output first
        self.alsa_stream_out = self.alsa_obj.open(
            format=FORMAT_ALSA, channels=1, rate=RATE, output=True,
            frames_per_buffer=ALSA_BUFFER_SIZE_MULTIPLIER*ALSA_BUFFER_SIZE,
            output_device_index=DEVICE_NUMBER,
            )
        self.play_sine_queue = multiprocessing.Queue()
        self.sine_process = multiprocessing.Process(
            target=sinePlay,
            args=(self.play_sine_queue, self.alsa_stream_out)
            )
        self.sine_process.start()

        self.alsa_stream_in = self.alsa_obj.open(
            format=FORMAT_ALSA, channels=2, rate=RATE, input=True,
            frames_per_buffer=ALSA_BUFFER_SIZE_MULTIPLIER*ALSA_BUFFER_SIZE,
            input_device_index=DEVICE_NUMBER,
            )
        self.tascam_input_queue = multiprocessing.Queue()
        self.tascam_input_process = multiprocessing.Process(
            target=tascam_input,
            args=(self.tascam_input_queue, self.alsa_stream_in)
            )
        self.tascam_input_process.start()
        return self.play_sine_queue, self.tascam_input_queue

    def end(self):
        ### schedule clean-up
        self.play_sine_queue.put(-1)
        self.tascam_input_process.terminate()

        ### actual clean-up
        self.sine_process.join()
        self.alsa_stream_out.stop_stream()
        self.alsa_stream_out.close()

        self.tascam_input_process.join()
        self.alsa_stream_in.stop_stream()
        self.alsa_stream_in.close()


def test_run(freq_queue, audio_in_queue):
    ### testing: do something with data
    lefts = []
    rights = []
    seconds = 1.0
    for i in range(int(seconds*RATE/PROCESS_BUFFER_SIZE)):
        while audio_in_queue.empty():
            time.sleep(0.1)
        while not audio_in_queue.empty():
            left, right = audio_in_queue.get()
            lefts.append(left)
            rights.append(right)
    return lefts, rights

def test_display(lefts, rights):
    ### testing: do something with data
    ### show or save data?
    left_all = numpy.array(lefts).flatten()
    right_all = numpy.array(rights).flatten()

    import scipy.io.wavfile
    scipy.io.wavfile.write("test-right.wav", RATE,
        right_all)
    scipy.io.wavfile.write("test-left.wav", RATE,
        left_all)



def test():
    audio = Audio()
    audio.get_info()
    ### real
    freq_queue, audio_in_queue = audio.begin()
    lefts, rights = test_run(freq_queue, audio_in_queue)
    audio.end()
    test_display(lefts, rights)
    audio.close()

if __name__ == "__main__":
    test()

