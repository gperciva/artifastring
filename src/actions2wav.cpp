/*
 * Copyright 2010--2011 Graham Percival
 * This file is part of Artifastring.
 *
 * Artifastring is free software: you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version.
 *
 * Artifastring is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public
 * License along with Artifastring.  If not, see
 * <http://www.gnu.org/licenses/>.
 */

#include "artifastring_instrument.h"
#include "monowav.h"

// This file is ugly and stupid, but it works.  And "if it's
// stupid and it works, it's not stupid" -somebody.
// So I guess this file is just ugly.  :)

#include <stdio.h>
#include <stdlib.h>

#include <string>
#include <vector>
#include <fstream>

#include <iostream>
#include <sstream>

using namespace std;
unsigned int total_samples;

vector<string> gulp_file(const char *filename) {
    vector<string> input;
    input.clear();

    string line;
    ifstream input_file(filename, ios_base::in);
    while (getline(input_file, line)) {
        input.push_back(line);
    }
    return input;
}

inline void waitUntil(ArtifastringInstrument *violin, MonoWav *wavfile,
                      MonoWav *forces_file, float until)
{
    int delta = until*ARTIFASTRING_INSTRUMENT_SAMPLE_RATE - total_samples;
    if (delta > 0) {
        // make sure we can easily deal with forces
        delta = HAPTIC_DOWNSAMPLE_FACTOR*(delta/HAPTIC_DOWNSAMPLE_FACTOR);
        //cout<<"get audio space for: "<<delta<<endl;
        short *array = wavfile->request_fill(delta);
        //cout<<"get force space for: "<<delta/4<<endl;
        // FIXME: test with full force buffer
        //short *forces = forces_file->request_fill(delta/HAPTIC_DOWNSAMPLE_FACTOR);
        //short *forces = forces_file->request_fill(delta);
        int unsafe = violin->wait_samples_forces(array, NULL, delta);
        if (unsafe > 0) {
            //printf("#Unsafe: friction skip over stable, num samples: %i\n",
            //    unsafe);
        }
        total_samples += delta;
    } else {
        if (delta < 0) {
            printf("ERROR: going back in time!\n");
            printf("  now: %f, requested: %f\n",
                   double(total_samples)/ARTIFASTRING_INSTRUMENT_SAMPLE_RATE, until);
            exit(1);
        }
    }
}

void command_finger(ArtifastringInstrument *violin, MonoWav *wavfile,
                    MonoWav *forces_file, string command)
{
    int num_tabs = 0;
    for (unsigned int i=0; i < command.length(); i++) {
        if (command[i] == '\t') {
            num_tabs++;
        }
    }
    float next_time;
    int which_string;
    float finger_position;
    if (num_tabs == 3) {
        sscanf(command.c_str(), "f\t%f\t%i\t%f",
               &next_time, &which_string, &finger_position);
        waitUntil(violin, wavfile, forces_file, next_time);
        violin->finger(which_string, finger_position);
    } else if (num_tabs == 4) {
        float spring_K;
        sscanf(command.c_str(), "f\t%f\t%i\t%f\t%f",
               &next_time, &which_string, &finger_position, &spring_K);
        waitUntil(violin, wavfile, forces_file, next_time);
        violin->finger(which_string, finger_position, spring_K);
    } else {
        printf("Badly formed finger line in .actions file\n");
    }
}

void command_reset(ArtifastringInstrument *violin, MonoWav *wavfile,
                   MonoWav *forces_file, string command)
{
    float next_time;
    sscanf(command.c_str(), "r\t%f", &next_time);
    waitUntil(violin, wavfile, forces_file, next_time);
    violin->reset();
}


void command_wait(ArtifastringInstrument *violin, MonoWav *wavfile,
                  MonoWav *forces_file, string command)
{
    float next_time;
    sscanf(command.c_str(), "w\t%f", &next_time);
    waitUntil(violin, wavfile, forces_file, next_time);
}

void command_pluck(ArtifastringInstrument *violin, MonoWav *wavfile,
                   MonoWav *forces_file, string command)
{
    float next_time;
    int which_string;
    float pluck_position;
    float pluck_force;
    sscanf(command.c_str(), "p\t%f\t%i\t%f\t%f", &next_time,
           &which_string, &pluck_position, &pluck_force);
    waitUntil(violin, wavfile, forces_file, next_time);
    //printf("actions2wav, pluck force: %g\n", pluck_force);
    violin->pluck(which_string, pluck_position, pluck_force);
}

void command_bow(ArtifastringInstrument *violin, MonoWav *wavfile,
                 MonoWav *forces_file, string command)
{
    float next_time;
    int which_string;
    float bow_position, force, velocity;
    sscanf(command.c_str(), "b\t%f\t%i\t%f\t%f\t%f", &next_time,
           &which_string, &bow_position, &force, &velocity);
    waitUntil(violin, wavfile, forces_file, next_time);
    violin->bow(which_string, bow_position, force, velocity);
}

void command_bow_accel(ArtifastringInstrument *violin, MonoWav *wavfile,
                       MonoWav *forces_file, string command)
{
    float next_time;
    int which_string;
    float bow_position, force, velocity, accel;
    sscanf(command.c_str(), "a\t%f\t%i\t%f\t%f\t%f\t%f", &next_time,
           &which_string, &bow_position, &force, &velocity, &accel);
    waitUntil(violin, wavfile, forces_file, next_time);
    violin->bow_accel(which_string, bow_position, force, velocity, accel);
}


void play_file(vector<string> input, string wav_filename,
               string forces_filename, string log_filename,
               InstrumentType instrument_type, int instrument_number)
{
    ArtifastringInstrument *violin = new ArtifastringInstrument(instrument_type, instrument_number);
    MonoWav *wavfile = new MonoWav(wav_filename.c_str(),
                                   4096, ARTIFASTRING_INSTRUMENT_SAMPLE_RATE);
    //MonoWav *forces_file = new MonoWav(forces_filename.c_str(),
    //                                   4096, ARTIFASTRING_INSTRUMENT_SAMPLE_RATE / HAPTIC_DOWNSAMPLE_FACTOR);
    MonoWav *forces_file = NULL;


#ifdef RESEARCH
    /*
        for (int string_number=0; string_number<4; string_number++) {
            char filename[1024];
            sprintf(filename, log_filename.c_str(), string_number);
            violin->set_string_logfile(string_number, filename);
        }
        */
#else
    (void) log_filename;
#endif

    total_samples = 0;

    for (unsigned int i=0; i<input.size(); i++) {
        switch (input[i][0]) {
        case '#':
            // comment line; do nothing
            break;
        case 'r':
            command_reset(violin, wavfile, forces_file, input[i]);
            break;
        case 'w':
            command_wait(violin, wavfile, forces_file, input[i]);
            break;
        case 'f':
            command_finger(violin, wavfile, forces_file, input[i]);
            break;
        case 'b':
            command_bow(violin, wavfile, forces_file, input[i]);
            break;
        case 'a':
            command_bow_accel(violin, wavfile, forces_file, input[i]);
            break;
        case 'p':
            command_pluck(violin, wavfile, forces_file, input[i]);
            break;
        case '\n':
            break;
        case 0:
            break;
        default:
            printf("Unrecognized command: ");
            cout<<input[i][0]<<endl;
            //printf("%i\n", input[i][0]);
        }
    }
    delete violin;
    delete wavfile;
    //delete forces_file;
}



int main(int argc, char **argv) {
    if (argc < 2) {
        printf("Usage: ./action2wav FILENAME.action");
        printf(" {{INSTRUMENT_TYPE}} {{INSTRUMENT_NUMBER}} {{SAFE}}\n");
    } else {
        string filename = argv[1];
        int instrument_type = 0;
        int instrument_number = 0;
        if (argc > 2) {
            instrument_type = atoi(argv[2]);
        }
        if (argc > 3) {
            instrument_number = atoi(argv[3]);
        }

        vector<string> input = gulp_file(filename.c_str());
        size_t suffix_position = filename.find(".actions");
        if (suffix_position == string::npos) {
            printf("File should end in .actions\n");
            exit(2);
        }
        string wav_filename = filename;
        wav_filename.replace(suffix_position, 8, ".wav");
        string forces_filename = filename;
        forces_filename.replace(suffix_position, 8, ".forces.wav");
        string log_filename = filename;
        log_filename.replace(suffix_position, 8, ".string-%i.log");

        play_file(input, wav_filename, forces_filename,
                  log_filename,
                  (InstrumentType)instrument_type, instrument_number);

    }
}
