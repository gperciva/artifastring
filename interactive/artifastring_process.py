#!/usr/bin/env python

### load artifastring from build dir if exists
import sys
sys.path.append('../build/swig')
sys.path.append('../build/.libs')

import artifastring_instrument
ARTIFASTRING_SAMPLE_RATE = artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE
HAPTIC_DOWNSAMPLE_FACTOR = artifastring_instrument.HAPTIC_DOWNSAMPLE_FACTOR

import actions_file
import collections

import enum
COMMANDS = enum.enum('BOW', 'FINGER', 'TENSION', 'UNSAFE', 'RESET')

ArtifastringInit = collections.namedtuple('ArtifastringInit', """
    instrument_type,
    instrument_number,
    """)

HOPSIZE = 512


import os
### portaudio should use plughw
os.environ['PA_ALSA_PLUGHW'] = '1'
import pyaudio

def make_audio_stream():
    pyaudio_obj = pyaudio.PyAudio()
    audio_stream = pyaudio_obj.open(
        rate = ARTIFASTRING_SAMPLE_RATE,
        channels = 1,
        format = pyaudio.paInt16,
        input=False,
        output = True,
        #output_device_index = 0,
        frames_per_buffer=HOPSIZE,
        )
    return pyaudio_obj, audio_stream

def handle_command(violin, commands_pipe, logfile, samples):
    command = commands_pipe.recv()
    #print command
    params = command[1]
    if command[0] == COMMANDS.BOW:
        violin.bow(params.violin_string, params.bow_position,
               params.force, params.velocity)
        logfile.bow(
            float(samples)/ARTIFASTRING_SAMPLE_RATE,
            params.violin_string,
            params.bow_position, params.force, params.velocity,
            0 # bow_pos_along
            )
    elif command[0] == COMMANDS.FINGER:
        violin.finger(params.violin_string, params.finger_position)
        logfile.finger(
            float(samples)/ARTIFASTRING_SAMPLE_RATE,
            params.violin_string,
            params.finger_position)
    elif command[0] == COMMANDS.TENSION:
        if params.tension_relative != 1.0:
            pc = violin.get_physical_constants(params.violin_string)
            pc.T *= params.tension_relative
            commands_pipe.send( (COMMANDS.TENSION, pc.T) )
            violin.set_physical_constants(params.violin_string, pc)
    elif command[0] == COMMANDS.RESET:
        violin.reset()


def violin_process(artifastring_init, commands_pipe, audio_pipe):
    try:
        pyaudio_obj, audio_stream = make_audio_stream()
    except:
        pyaudio_obj = None
        audio_stream = None

    violin = artifastring_instrument.ArtifastringInstrument(
        artifastring_init.instrument_type,
        artifastring_init.instrument_number)
    samples = 0

    logfile = actions_file.ActionsFile("log-interactive.actions")
    while commands_pipe.poll():
        handle_command(violin, commands_pipe, logfile, samples)

    #pc = violin.get_physical_constants(params.violin_string)
    #commands_pipe.send( (TENSION, pc.T) )

    while True:
        while commands_pipe.poll():
            handle_command(violin, commands_pipe, logfile, samples)
        arr, forces = audio_pipe.recv()
        if arr is None:
            # poison pill
            break
        violin.wait_samples_forces_python(arr, forces)
        #unsafe = violin.wait_samples_forces_python(arr, forces)
        #params_log.write("unsafe: %i" % unsafe)
        #commands_pipe.send( (COMMANDS.UNSAFE, unsafe) )
        if audio_stream is not None:
            audio_stream.write( arr.tostring(), HOPSIZE )
        audio_pipe.send( (arr, forces) )
        samples += HOPSIZE
    logfile.wait(float(samples)/ARTIFASTRING_SAMPLE_RATE)
    logfile.close()

    if pyaudio_obj is not None:
        audio_stream.close()
        pyaudio_obj.terminate()

