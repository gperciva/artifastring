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

#include "violin_instrument.h"
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

inline void waitUntil(ViolinInstrument *violin, MonoWav *wavfile,
    MonoWav *forces_file, float until)
{
    int delta = until*44100.0 - total_samples;
    if (delta > 0) {
        short *array = wavfile->request_fill(delta);
        short *forces = forces_file->request_fill(delta);
        violin->wait_samples_forces(array, forces, delta);
        total_samples += delta;
    } else {
        if (delta < 0) {
            printf("ERROR: going back in time!\n");
            printf("  now: %f, requested: %f\n",
                   total_samples/44100.0, until);
            exit(1);
        }
    }
}

void command_finger(ViolinInstrument *violin, MonoWav *wavfile,
    MonoWav *forces_file, string command)
{
    float next_time;
    int which_string;
    float finger_position;
    sscanf(command.c_str(), "f\t%f\t%i\t%f",
           &next_time, &which_string, &finger_position);
    waitUntil(violin, wavfile, forces_file, next_time);
    violin->finger(which_string, finger_position);
}

void command_wait(ViolinInstrument *violin, MonoWav *wavfile,
    MonoWav *forces_file, string command)
{
    float next_time;
    sscanf(command.c_str(), "w\t%f", &next_time);
    waitUntil(violin, wavfile, forces_file, next_time);
}

void command_pluck(ViolinInstrument *violin, MonoWav *wavfile,
    MonoWav *forces_file, string command)
{
    float next_time;
    int which_string;
    float pluck_position;
    float pluck_force;
    sscanf(command.c_str(), "p\t%f\t%i\t%f\t%f", &next_time,
           &which_string, &pluck_position, &pluck_force);
    waitUntil(violin, wavfile, forces_file, next_time);
    violin->pluck(which_string, pluck_position, pluck_force);
}

void command_bow(ViolinInstrument *violin, MonoWav *wavfile,
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


void play_file(vector<string> input, MonoWav *wavfile, 
        MonoWav *forces_file, int instrument_number) {
    ViolinInstrument *violin = new ViolinInstrument(instrument_number);
    total_samples = 0;

    for (unsigned int i=0; i<input.size(); i++) {
        switch (input[i][0]) {
        case '#':
            // comment line; do nothing
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
        case 'p':
            command_pluck(violin, wavfile, forces_file, input[i]);
            break;
        default:
            printf("Unrecognized command: ");
            cout<<input[i][0]<<endl;

        }
    }
    delete violin;
}



int main(int argc, char **argv) {
    if (argc < 2) {
        printf("Usage: ./action2wav FILENAME.action {{INSTRUMENT_NUMBER}}\n");
    } else {
        string filename = argv[1];
        int instrument_number = 0;
        if (argc > 2) {
            instrument_number = atoi(argv[2]);
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
        forces_filename.replace(suffix_position, 8, ".forces");

        MonoWav *wavfile = new MonoWav(wav_filename.c_str(),4096);
        MonoWav *forces_file = new MonoWav(forces_filename.c_str(),4096);

        play_file(input, wavfile, forces_file, instrument_number);

        delete wavfile;
        delete forces_file;
    }
}
