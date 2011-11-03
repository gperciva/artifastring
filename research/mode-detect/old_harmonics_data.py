
        #plots(basename, dirname, self.filtereds, self.harmonicss,
        #    self.hop_rate, self.tnss, self.filenames)

    def plot_decays(self, tss, tns, harmonics, png_filename, instrument_string,
            start, end, name):
        if start >= len(harmonics):
            return
        pylab.figure()
        for i in range(start, end):
            if i >= len(harmonics):
                break
            ts = tss[i]
            tn = tns[i]
            if tn is None:
                continue
            color = matplotlib.cm.jet(float(i-start)/(end-start))
            pylab.plot(ts, harmonics[i],
                #'.', color=color, label="harmonic %i" % (i+1))
                '.', color=color, label="%i" % (i+1))
            # Demoucron, p. 60
            gradient = tn
            test_formula = map(lambda t: math.exp(-gradient*t), ts)
            pylab.plot(ts, test_formula,
            #    #'-', color=color, label="predict %i" % (i+1))
                '-', color=color)
        pylab.legend()
        #pylab.ylim([1e-6, 1e-2])
        pylab.xlabel("Time (seconds)")
        pylab.ylabel("Relative strength of harmonic")
        pylab.title("Decay envelopes and linear-fit lines, %s" %
            instrument_string)
        pylab.savefig(png_filename.replace(".png",
            str("-%s-decays.png" % name)))
        #if SHOW_DECAY:
        #    pylab.show()
 




###############################################


            continue

            for i, tn in enumerate(tns):
                if tn is None:
                    continue
                gradient = tn[0]
                end_hops = tn[1]
                if end_hops < defs.HARMONIC_DECAY_TIME_SECONDS / hop_rate:
                    tns[i] = None
                else:
                    tns[i] = gradient
            #    print i, tns[i]
                #if tns[i] == 0:
                #    exit(1)

            tnss.append(tns)
            tsss.append(tss)
            lenss.append(lens_harms)
            #for i, h in enumerate(tss):
            #    print len(h),
            #print
            #for i, h in enumerate(tns):
            #    print "%.2g" % h,
            #print
            #png_filename = os.path.join(png_dirname,
            #        wav_basename.replace(".wav", ".png"))
            #instrument_string = os.path.basename(wav_filename)
            #for i, name in enumerate(['a', 'b', 'c', 'd']):
            #    bail = True
            #    for j in range(5*i, 5*(i+1)):
            #        if len(harmonics[j]) > 0:
            #            bail = False
            #            break
            #    if bail:
            #        continue
                #self.plot_decays(tss, tns, harmonics, png_filename,
                #    instrument_string, 5*i, 5*(i+1), name)
            harmonicss.append(list(harmonics))

        if defs.HARMONICS_PLOT:
            for i, tns in enumerate(tnss):
                color = matplotlib.cm.jet(float(i)/len(tnss))
                pylab.plot(
                    numpy.arange(1, len(tns)+1),
                    tns, '.',
                    label=str(i+1),
                    color=color)
            pylab.xlim([0, 30])
            pylab.legend()
            pylab.show()
        #if PLOT_STFT or PLOT_TRUNCATED_LISTS:
        #    pylab.show()
        #pylab.show()
        filtereds = []


###############################################


# get list of sample (hop) times
# list of times = ts; list of list of times = tss
def get_tss(hop_rate, harmonics):
    tss = []
    for i in range(len(harmonics)):
        ts = get_ts(hop_rate, harmonics[i])
        tss.append(ts)
    return tss

def get_column(basename):
    col = 0
    if "fingerboard" in basename:
        col = 1
    elif "half" in basename:
        col = 2
    elif "third" in basename:
        col = 3
    elif "golden" in basename:
        col = 4
    elif "low2" in basename:
        col = 5
    elif "11.25" in basename:
        col = 6
    return col

def get_row(basename):
    row = 0
    if "hard" in basename:
        row = 1
    elif "soft" in basename:
        row = 2
    elif "tissue" in basename:
        row = 3
    elif "hair" in basename:
        row = 4
    elif "platic" in basename:
        row = 5
    return row

ALPHA = 0.5
PLOT_BON_DATA = True
PLOT_BON_LINES = True
def bon_odori_color(basename):
    #print basename
    col = get_column(basename)
    row = get_row(basename)
    #if "half" in basename:
    #    return "white"
    #elif "low2" in basename:
    #    return "yellow"
    #else:
    #    return "cyan"
    C = 0
    R = 1
    color_number = C * ((col-1)/5.0) + R * ((row-1)/4.0)
    color = matplotlib.cm.jet(color_number)
    return color

def plots(basename, dirname, filtereds, harmonicss, hop_rate, tnss,
        filenames):

    flatted_ts = []
    flatted_tns = []
    flatted_harms = []
    min_length = 20
    num_harms = 0
    for i in range(len(harmonicss)):
        for j in range(len(harmonicss[i])):
            if len(harmonicss[i][j]) > min_length:
                if num_harms < j:
                    num_harms = j
    for i in range(num_harms):
        flatted_ts.append([])
        flatted_harms.append([])
        for j, harm in enumerate(harmonicss):
            h = harm[i]
            if len(h) > min_length:
                ts = get_ts(hop_rate, h)
                flatted_ts[i].extend(ts)
                flatted_harms[i].extend(h)
        #print flatted_harms[i]
        tns = HarmonicsData.fit_to_exponential( (flatted_ts[i], flatted_harms[i]) )
        flatted_tns.append(tns)
        #if tns is not None:
        #    print i, -tns


    png_dirname = os.path.join(dirname, 'png')
    ### plot filtered but unprocessed
    min_length = 20
    num_harms = 0
    for i in range(len(filtereds)):
        for j in range(len(filtereds[i])):
            if len(filtereds[i][j]) > min_length:
                if num_harms < j:
                    num_harms = j
    for i in range(num_harms):
        png_filename = os.path.join(png_dirname,
            basename + "-modes-absolute-%02i.png" % (i+1))
        pylab.figure()
        for j, harm in enumerate(filtereds):
            h = harm[i]
            if HarmonicsData.num_non_zero(h) > min_length:
                #print "drawing harmonic", i, j
                ts = get_ts(hop_rate, h)
                color = matplotlib.cm.jet(float(j)/(num_harms))
                pylab.plot(ts, h, '.', color=color,
                    label="Pluck %i" % (j+1))
        pylab.xlabel("Time (seconds)")
        #pylab.ylabel("Relative spectral power")
        pylab.ylabel("Spectral power")
        pylab.title("Mode %02i" % (i+1))
        #pylab.legend()
        pylab.savefig(png_filename)
    ### plot filtered and processed
    min_length = 20
    num_harms = 0
    for i in range(len(harmonicss)):
        for j in range(len(harmonicss[i])):
            if len(harmonicss[i][j]) > min_length:
                if num_harms < j:
                    num_harms = j
    for i in range(num_harms):
        png_filename = os.path.join(png_dirname,
            basename + "-modes-relative-%02i.png" % (i+1))
        pylab.figure()
        for j, harm in enumerate(harmonicss):
            h = harm[i]
            #high_len = 0
            #high_ts = 0
            if len(h) > min_length:
                #print "drawing harmonic", i, j
                ts = get_ts(hop_rate, h)
                #if len(ts) > high_len:
                #    high_len = len(ts)
                #    high_ts = list(ts)
                #color = matplotlib.cm.jet(float(j)/(len(harmonicss)))
                #color = bon_odori_color(filenames[j])
                # HACK: for positions
                pos = int(j/3)
                color = matplotlib.cm.jet( pos / 3.0 )
                #print pos, color
                if PLOT_BON_DATA:
                    pylab.plot(ts, h, '-', color=color,
                        alpha=ALPHA,
                        label="Pluck %i" % (j+1))

                if tnss[j][i] is None:
                    continue
                gradient = tnss[j][i]
                predicted = numpy.exp(-gradient*numpy.array(ts))
                if PLOT_BON_LINES:
                    pylab.plot(ts,
                        predicted,
                        '-', color=color,
                        alpha=ALPHA,
                    )
        if flatted_tns[i] is not None:
            gradient = flatted_tns[i]
            #print gradient
            # UNSAFE RELY: use old ts
            #ts = get_ts(hop_rate, h)
            #print high_ts
            predicted = numpy.exp(-gradient*numpy.array(ts))
            pylab.plot(ts,
                predicted,
                '-',
                color='black',
                #color=color,
                #alpha=ALPHA,
            )
        pylab.xlabel("Relative time since maximum power (seconds)")
        pylab.ylabel("Relative spectral power")
        pylab.title("Mode %02i (processed for relative)" % (i+1))
        #pylab.legend()
        pylab.savefig(png_filename)





