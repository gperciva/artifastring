/*
 * Copyright 2010--2013 Graham Percival
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

#include "actions_file.h"
#include <string.h>

const int MAX_LINE_LENGTH = 2048;

ActionsFile::ActionsFile(const char *filename, int buffer_size)
{
    size = buffer_size;
    data = new ActionData[size];
    index = 0;
    outfile = fopen(filename, "w");
}

ActionsFile::~ActionsFile()
{
    close();
}

void ActionsFile::close()
{
    if (outfile != NULL) {
        writeBuffer();
        fclose(outfile);
        delete [] data;
        outfile = NULL;
    }
}

void ActionsFile::wait(float seconds) {
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_WAIT;
    action.seconds = seconds;
    data[index] = action;
    index++;
}

void ActionsFile::skipStart(float seconds) {
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_SKIPSTART;
    action.seconds = seconds;
    data[index] = action;
    index++;
}

void ActionsFile::skipStop(float seconds) {
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_SKIPSTOP;
    action.seconds = seconds;
    data[index] = action;
    index++;
}

void ActionsFile::finger(float seconds, int string_number,
                         float position)
{
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_FINGER;
    action.seconds = seconds;
    action.string_number = string_number;
    action.position = position;
    data[index] = action;
    index++;
}

void ActionsFile::category(float seconds, float category)
{
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_CATEGORY;
    action.seconds = seconds;
    action.force = category; // abuse of syntax
    data[index] = action;
    index++;
}

void ActionsFile::pluck(float seconds, int string_number,
                        float position, float force)
{
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_PLUCK;
    action.seconds = seconds;
    action.string_number = string_number;
    action.position = position;
    action.force = force;
    data[index] = action;
    index++;
}

void ActionsFile::bow(float seconds, int string_number,
                      float position, float force, float velocity,
                      float bow_pos_along)
{
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_BOW;
    action.seconds = seconds;
    action.string_number = string_number;
    action.position = position;
    action.force = force;
    action.velocity = velocity;
    action.position_along = bow_pos_along;
    data[index] = action;
    index++;
}

void ActionsFile::accel(float seconds, int string_number,
                        float position, float force, float velocity,
                        float bow_pos_along, float accel)
{
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_ACCEL;
    action.seconds = seconds;
    action.string_number = string_number;
    action.position = position;
    action.force = force;
    action.velocity = velocity;
    action.position_along = bow_pos_along;
    action.accel = accel;
    data[index] = action;
    index++;
}

void ActionsFile::comment(const char *text)
{
    writeBuffer();
    char textline[MAX_LINE_LENGTH];
    sprintf(textline, "#\t%.*s\n", MAX_LINE_LENGTH-1, text);
    fwrite(textline, sizeof(char), strlen(textline), outfile);
}

void ActionsFile::writeBuffer()
{
    for (int i = 0; i < index; i++) {
        ActionData actions = data[i];
        char textline[MAX_LINE_LENGTH];

        switch (actions.type) {
        case ACTION_WAIT:
            sprintf(textline, "w\t%f\n",
                    actions.seconds);
            break;
        case ACTION_SKIPSTART:
            sprintf(textline, "s\t%f\n",
                    actions.seconds);
            break;
        case ACTION_SKIPSTOP:
            sprintf(textline, "k\t%f\n",
                    actions.seconds);
            break;
        case ACTION_FINGER:
            sprintf(textline, "f\t%f\t%i\t%f\n",
                    actions.seconds,
                    actions.string_number, actions.position);
            break;
        case ACTION_PLUCK:
            sprintf(textline, "p\t%f\t%i\t%f\t%f\n",
                    actions.seconds,
                    actions.string_number, actions.position,
                    actions.force);
            break;
        case ACTION_BOW:
            sprintf(textline, "b\t%f\t%i\t%f\t%f\t%f\t%f\n",
                    actions.seconds,
                    actions.string_number, actions.position,
                    actions.force, actions.velocity,
                    actions.position_along);
            break;
        case ACTION_ACCEL:
            sprintf(textline, "a\t%f\t%i\t%f\t%f\t%f\t%f\t%f\n",
                    actions.seconds,
                    actions.string_number, actions.position,
                    actions.force, actions.velocity,
                    actions.accel,
                    actions.position_along);
            break;
        case ACTION_CATEGORY:
            sprintf(textline, "cat\t%f\t%f\n",
                    actions.seconds,
                    actions.force); // abuse of syntax
            break;
        }
        fwrite(textline, sizeof(char), strlen(textline), outfile);
    }
    index = 0;
}

