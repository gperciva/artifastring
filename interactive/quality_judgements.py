#!/usr/bin/env python

import os
import midi_pos

TRAIN_DIR = "train"

SUBDIRS = True

CATEGORIES_CENTER_OFFSET = 3
CATEGORY_POSITIVE_OFFSET = 100

class TrainInfo:
    pass

def training_init(train_dirname, artifastring_init):
    train_info = TrainInfo()
    if train_dirname is None:
        base_dirname = TRAIN_DIR
    else:
        base_dirname = train_dirname
    if SUBDIRS:
        for inst_text in ['violin', 'viola', 'cello']:
            dirname = os.path.join(base_dirname, inst_text)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        train_info.train_dirname = os.path.join(base_dirname,
            inst_type_name(artifastring_init))
    else:
        if not os.path.exists(base_dirname):
            os.makedirs(base_dirname)
        train_info.train_dirname = base_dirname
    return train_info

def _key_to_cat(cat_key):
    return int(cat_key) - CATEGORIES_CENTER_OFFSET

def inst_type_name(artifastring_init):
    if artifastring_init.instrument_type == 0:
        return "violin"
    if artifastring_init.instrument_type == 1:
        return "viola"
    if artifastring_init.instrument_type == 2:
        return "cello"

def inst_name(artifastring_init):
    if artifastring_init.instrument_type == 0:
        return "violin-%i" % artifastring_init.instrument_number
    if artifastring_init.instrument_type == 1:
        return "viola-%i" % artifastring_init.instrument_number
    if artifastring_init.instrument_type == 2:
        return "cello-%i" % artifastring_init.instrument_number


def get_train_basename(train_info, artifastring_init, params):
    finger_midi = midi_pos.pos2midi(params.finger_position)
    filename_count = 1
    while True:
        basename = "%s_%i_%.3f_%.3f_%.3f_%.3f_%i" % (
            os.path.join(train_info.train_dirname,
                inst_name(artifastring_init)),
            params.violin_string,
            finger_midi,
            params.bow_position,
            params.force,
            params.velocity,
            filename_count)
        if not os.path.exists(basename+".wav"):
            break
        filename_count += 1
    return basename

def _get_mf_filename(train_info, params):
    mf_filename = os.path.join(train_info.train_dirname,
        str("%i.mf" % params.violin_string))
    return mf_filename

def append_to_mf(train_info, params, wav_filename, cat_key):
    cat = _key_to_cat(cat_key)
    mf_filename = _get_mf_filename(train_info, params)
    mf_file = open(mf_filename, 'a')
    mf_file.write(str("%s\t%03i\n" % (wav_filename,
        cat + CATEGORY_POSITIVE_OFFSET)) )
    mf_file.close()

