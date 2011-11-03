#!/usr/bin/env python

import sys
sys.path.append("../shared/")

import os

import harmonics_data

import sys
import mode_decays

import published_constants
import adjust_decays
import tables

# no clue why I need this.  :(
from harmonics_data import HarmonicsStats


def process(dirname, basename, recalc=False, plot=False):
    inst = basename.split('-')[0]
    st = basename.split('-')[1]
    pc = published_constants.PHYSICAL_CONSTANT_RANGES[inst]
    # find average tension, length
    T = ( pc[st]['T'][0] + pc[st]['T'][1] ) / 2
    L = ( pc['L'][0] + pc['L'][1] ) / 2
    #print T, L

    harms = harmonics_data.HarmonicsData(dirname, basename)
    decays, f0, B, harm_stats = harms.get_data()

    nf, nb, stats = mode_decays.handle_decays(decays,
        basename, f0, B, T, L, harm_stats,
        plot=plot, recalc=recalc)
    return nf, nb, stats, harm_stats

def get_header():
    fields = ["name", "B1", "B2", "$R^2$",
        "notes", "alpha 1", "alpha 2", "alpha 3",
        "alpha 4", "alpha 5", "alpha 10"]
    return '\t'.join(fields)

def get_info(basename, nf, nb, stats):
    notes = adjust_decays.notes_decays(basename)
    text = "%s\t%.3g\t%.3g\t%.2f\t%s\t%.1f\t%.1f\t%.1f\t%.1f\t%.1f\t%.1f" % (
        tables.anonymize_name(basename),
        nf, nb,
        stats.rsquared,
        notes,
        stats.alpha_1, stats.alpha_2, stats.alpha_3,
        stats.alpha_4, stats.alpha_5,
        stats.alpha_10,
        )
    return text

def get_stats_header():
    fields = ["name", "total partials",
        "max not above noise",
        "num not above noise",
        "not sufficient drop",
        "high variance",
        "cannot fit",
        "low $R^2$",
        "decays used", "highest mode", "notes"]
    return '\t'.join(fields)

def get_stats_info(basename, stats):
    notes = adjust_decays.notes_removing(basename)
    text = "%s\t%i\t%i\t%i\t%i\t%i\t%i\t%i\t%i\t%i\t%s" % (
        tables.anonymize_name(basename),
        stats.num_harms_original,
        stats.num_harms_max_no_above_noise,
        stats.num_harms_num_no_above_noise,
        stats.num_harms_no_drop,
        stats.num_harms_no_variance,
        stats.num_harms_no_fit,
        stats.num_harms_no_rsquared,
        stats.num_harms_end,
        stats.highest_harm,
        notes,
        )
    return text

if __name__ == "__main__":
    try:
        #dirname = sys.argv[1]
        dirname = "yvr"
        basename = sys.argv[1]
    except:
        print "biology.py DIRNAME BASENAME"
    if not os.path.isdir("out"):
        os.makedirs("out")

    nf, nb, stats, harm_stats = process(dirname, basename, plot=True)
    print get_header()
    print get_info(basename, nf, nb, stats)
    print
    print get_stats_header()
    print get_stats_info(basename, harm_stats)


