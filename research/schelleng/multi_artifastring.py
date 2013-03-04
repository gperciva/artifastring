#!/usr/bin/env python

NUM_PROCESSES = 4

import sys
sys.path.append('../../build/swig')
sys.path.append('../../build/.libs')

import multiprocessing


def chunkify(items, num):
    #return zip(*[iter(items)]*chunks)
    return [items[i::num] for i in range(num)]


def wrap_worker_func(ci, result_queue, shared_init_func, shared_init_args, worker_func, chunk):
    #print "worker %i, chunk length: %i" % (ci, len(chunk))
    #print chunk, shared_init_func
    shared = shared_init_func(*shared_init_args)
    #shared = None
    for args in chunk:
        result = worker_func(shared, *args)
        #print ci, result[0][0]
        result_queue.put(result)

def task(worker_func, argslist, shared_init_func, shared_init_args,
        disable_multi=False):
    #if inst_type == 0:
    #    inst_type = artifastring_instrument.Violin
    #elif inst_type == 1:
    #    inst_type = artifastring_instrument.Viola
    #elif inst_type == 2:
    #    inst_type = artifastring_instrument.Cello

    pool = multiprocessing.Pool(processes=NUM_PROCESSES)
    manager = multiprocessing.Manager()
    result_queue = manager.Queue()
    chunks = chunkify(argslist, NUM_PROCESSES)
    for ci, chunk in enumerate(chunks):
        #print "worker %i, chunk length: %i" % (ci, len(chunk))
        if disable_multi:
            wrap_worker_func(ci,
                result_queue, shared_init_func, shared_init_args, worker_func, chunk)
        else:
            pool.apply_async(wrap_worker_func,
                args=(ci, result_queue, shared_init_func,
                shared_init_args, worker_func, chunk))
    pool.close()
    pool.join()
    return result_queue



