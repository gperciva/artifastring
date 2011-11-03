#!/usr/bin/env python

import numpy
numpy.seterr(under='ignore')
import scipy.optimize
import scipy.stats
import pylab

import stft

def check_ok_fit(fit, rsquared, variance):
    if rsquared < 0.0 or variance == None:
        return None, None, None
    return fit, rsquared, variance


def fit_single_exponential(xs, yn, noise_mean,
        log=False, show=False, plot=False):
    def single_decay_constraints(C, A1, A2):
    #def single_decay_constraints(A1, A2):
        return numpy.array([
            (C > 0) - 1,
            (A1 > 0) - 1,
            (A2 > 0) - 1,
            ])
    def exponential_decay(x, C, A1, A2):
    #def exponential_decay(x, A1, A2):
        if any(single_decay_constraints( C, A1, A2 ) != 0):
        #if any(single_decay_constraints( A1, A2 ) != 0):
            return 1e9 * numpy.ones(len(x))
        values = C + A1*numpy.exp(-A2*x)
        #values = A1*numpy.exp(-A2*x)
        if log:
            return numpy.log(values)
        else:
            return values

    #noise_floor_pos = 0.9*len(yn)
    #linear_decay_pos = 0.1*len(yn)
    #noise_floor_pos = -1
    linear_decay_pos = 0.2*len(yn)
    #yn -= noise_mean
    if log:
        ys = numpy.log(yn)
        noise = noise_mean #yn[noise_floor_pos:].mean()
        rise = ys[linear_decay_pos] - ys[0]
        run = xs[linear_decay_pos] - xs[0]
        overall_single_slope = -(rise/run)
    else:
        ys = numpy.array(yn)
        #noise = scipy.stats.gmean(yn[noise_floor_pos:])
        noise = noise_mean #yn[noise_floor_pos:].mean()
        rise = ys[linear_decay_pos] - ys[0]
        run = xs[linear_decay_pos] - xs[0]
        try:
            overall_single_slope = -numpy.log(-(rise/run))
        except:
            overall_single_slope = 1.
    if overall_single_slope < 0:
        overall_single_slope = 1.
    amplitude = yn[0] - noise
    initial_guess = numpy.array([
        noise, amplitude, overall_single_slope,
        #amplitude, overall_single_slope,
    ])

    if show:
        print "single exponential, log ", log, " initial:", initial_guess
    single_fit, pcov = scipy.optimize.curve_fit(
        exponential_decay,
        xs, ys,
        initial_guess
        )
    # automatically handles logs
    predicted = exponential_decay(xs, *single_fit)

    if show:
        print "single exponential fit:", single_fit
    if plot:
        pylab.figure()
        pylab.plot(xs, ys, '.')
        pylab.plot(xs, predicted)
        pylab.title("Single exponential, log fit %s" % log)
        pylab.show()

    ss_err = ((ys - predicted)**2).sum()
    ss_tot = ((ys-ys.mean())**2).sum()
    rsquared = 1. - (ss_err / ss_tot)

    try:
        variance = pcov[2][2]
        #variance = pcov[1][1]
    except:
        variance = None

    return check_ok_fit(single_fit, rsquared, variance)


def fit_single_exponential_final(xs, ys, noise_y, decay,
        show=False, plot=False):
    def single_decay_constraints_fixed(amp1, alpha1):
        return numpy.array([
            (1 > amp1 > 0) - 1,
            (alpha1 > 0) - 1,
            ])
    def single_exponential_final(x, amp1, alpha1):
        if any(single_decay_constraints_fixed(amp1, alpha1) != 0):
            return numpy.ones(len(x))
        #return numpy.log(
        return (
            noise_y + amp1*numpy.exp(-alpha1*x)
            )

    initial_guess = numpy.array([
        ys[0]-noise_y, decay,
    ])

    if show:
        print "single exponential fixed, initial:", initial_guess
    fit, pcov = scipy.optimize.curve_fit(
            single_exponential_final,
            #xs, numpy.log(ys),
            xs, ys,
            initial_guess,
            #Dfun=diff_single_exponential_final, col_deriv=1,
        )
    if show:
        print "single exponential fit:", fit

    predicted = single_exponential_final(xs, *fit)
    #ys = numpy.log(ys)
    if show:
        pylab.figure()
        pylab.plot(ys)
        pylab.plot(predicted)
        pylab.show()

    ss_err = ((ys - predicted)**2).sum()
    ss_tot = ((ys-ys.mean())**2).sum()
    rsquared = 1. - (ss_err / ss_tot)
    ys = numpy.exp(ys)
    predicted = numpy.exp(predicted)

    try:
        variance = pcov[1][1]
    except:
        variance = None

    if show:
        print rsquared
        print "VAR:", variance
    if plot:
        pylab.figure()
        pylab.subplot(211)
        pylab.title(
            str("single exponential, fixed noise\nalpha:%.3f" %
            (fit[1])))
        pylab.plot(xs, stft.amplitude2db(ys), '.')
        pylab.plot(xs, stft.amplitude2db(predicted))
         
        pylab.subplot(212)
        pylab.plot(xs, ys, '.')
        pylab.plot (xs, predicted)
        pylab.show()

    return check_ok_fit(fit, rsquared, variance)

 
# this needs to be global for the testing function
def double_exponential_function_log(xs, noise_y, amp1, amp2, alpha1, alpha2):
    if any(double_exponential_constraints(
            noise_y, amp1, amp2, alpha1, alpha2) != 0):
        return numpy.ones(len(xs))
    return numpy.log(
        noise_y
        + amp1*numpy.exp(-alpha1*xs)
        + amp2*numpy.exp(-alpha2*xs)
        )

def double_exponential_constraints(noise_y, amp1, amp2, alpha1, alpha2):
    return numpy.array([
        (noise_y > 0) - 1,
        (1 >= amp1 > 0) - 1,
        (1 >= amp2 > 0) - 1,
        (alpha1 > 0) - 1,
        (alpha2 > 0) - 1,
        (alpha1 > alpha2) - 1,
        ])

def fit_double_exponential(xs, ys, fast_single_fit, slow_single_fit,
        show=False, plot=False):
    # swap fast and slow if necessary
    fast_amp = fast_single_fit[1]
    slow_amp = slow_single_fit[1]
    fast_decay = fast_single_fit[2]
    slow_decay = slow_single_fit[2]
    if fast_decay < slow_decay:
        fast_decay, slow_decay = slow_decay, fast_decay
        fast_amp, slow_amp = slow_amp, fast_amp

    initial_guess = numpy.array([
        slow_single_fit[0],
        fast_amp,
        slow_amp,
        fast_decay,
        slow_decay,
        ])
    
    if show:
        print "initial guess:\t", initial_guess
    fit, pcov = scipy.optimize.curve_fit(
        double_exponential_function_log,
        xs, numpy.log(ys),
        initial_guess
        )
    predicted = numpy.exp(double_exponential_function_log(xs, *fit))

    ss_err = ((ys - predicted)**2).sum()
    ss_tot = ((ys-ys.mean())**2).sum()
    rsquared = 1. - (ss_err / ss_tot)

    try:
        variance = pcov[2][2]
    except:
        variance = None

    if show:
        print "double fit:\t", fit
    if plot:
        pylab.figure()
        log = True
        if log:
            pylab.semilogy(xs, ys, '.')
            pylab.semilogy(xs, predicted)
        else:
            pylab.plot(xs, ys, '.')
            pylab.semilogy(xs, predicted)
        pylab.title("Double exponential")
        pylab.show()

    return check_ok_fit(fit, rsquared, variance)



def fit_best_exponential(xs, yn, noise_mean,
        show=False, plot=False, plot_last=False):
    if show:
        print
        print
    #show=True
    #plot=True
    slow_single_fit, rsquared, variance = fit_single_exponential(xs, yn,
        noise_mean,
        #log=False,
        log=True,
        show=show, plot=plot_last)

    fit, rsquared, variance = check_ok_fit(slow_single_fit, rsquared, variance)
    if fit is None:
        return None, None, None
    ## FIXME
    fit = [slow_single_fit[1], slow_single_fit[2], slow_single_fit[0]]
    return check_ok_fit(fit, rsquared, variance)

    #show=True
    #plot=True
    single_fit_curve, rsquared, variance = fit_single_exponential_final(xs, yn,
        slow_single_fit[0], slow_single_fit[2],
        show=show, plot=plot_last)

    fit = single_fit_curve
    return check_ok_fit(fit, rsquared, variance)

    if slow_single_fit is None:
        return None, None, None
    #fast_single_fit, rsquared, variance = fit_single_exponential(xs, yn,
    #    log=False,
    #    show=show, plot=plot)
    #if fast_single_fit is None:
    #    return None, None, None
    if show:
        print "slow:\t\t", slow_single_fit
        #print "fast:\t\t", fast_single_fit

    #try:
    #    double_fit, rsquared, variance = fit_double_exponential(
    #        xs, yn, fast_single_fit, slow_single_fit,
    #        show=show, plot=plot)
    #except:
    #    return None, None, None
    #if double_fit is None:
    #    return None, None, None

    single_fit_curve, rsquared, variance = fit_single_exponential_final(xs, yn,
        slow_single_fit[0], slow_single_fit[2],
        show=show, plot=plot_last)
        #double_fit[0], double_fit[3], show=show, plot=plot)
    if single_fit_curve is None:
        return None, None, None
    #fit = [double_fit[0], single_fit_curve[0], single_fit_curve[1]]
    fit = [slow_single_fit[0], single_fit_curve[0], single_fit_curve[1]]
    #fit = [slow_single_fit[0], slow_single_fit[1], slow_single_fit[2]]
    return check_ok_fit(fit, rsquared, variance)

def test():
    numpy.seterr(under='ignore')
    xs = numpy.linspace(0,20,1000)
    params = [9.5e-5, 0.04, 0.12, 4.87, 1.63]
    ys = numpy.exp(double_exponential_function_log(xs, *params))
    yn = ys + numpy.random.uniform(0, 1e-4, size=len(xs))

    fit, rsquared, variance = fit_best_exponential(xs, yn, show=True, plot=True, plot_last=True)
    if fit is None:
        print "Failed to find parameters!"

if __name__ == "__main__":
    test()


