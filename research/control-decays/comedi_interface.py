#!/usr/bin/env python

import comedi
DEVICE_FILENAME = "/dev/comedi0"
DIGITAL_OUTPUT_SUBDEVICE = 2
CHANNEL_RELAY = 7
CHANNEL_A0 = 0
CHANNEL_A1 = 1

class Comedi:

    def __init__(self):
        self.device = comedi.comedi_open(DEVICE_FILENAME)
        if not self.device:
            raise Exception("Cannot open device")
        self.initialize()

    def initialize(self):
        # configures channels for output
        for channel in [CHANNEL_RELAY, CHANNEL_A0, CHANNEL_A1]:
            ret = comedi.comedi_dio_config(self.device,
                DIGITAL_OUTPUT_SUBDEVICE, channel,
                comedi.COMEDI_OUTPUT)
            print "attempted to set output channel %i, return value:\t%i" %(
                channel, ret)

    def send(self, channel, value):
        ret = comedi.comedi_data_write(self.device, DIGITAL_OUTPUT_SUBDEVICE,
            channel, 0, 0, value)
        print "attempted to send channel %i data %i, return value:\t%i" %(
            channel, value, ret)
        return ret
    
    def send_all(self, value):
        for channel in [CHANNEL_RELAY, CHANNEL_A0, CHANNEL_A1]:
            self.send(channel, value)

def test(comedi):
    import time
    i = 0
    while True:
        comedi.send(CHANNEL_A0, i & 1)
        comedi.send(CHANNEL_A1, (i & 2) >> 1)
        comedi.send(CHANNEL_RELAY, (i&4) >> 2)
        time.sleep(1)
        i += 1

if __name__ == "__main__":
    comedi_obj = Comedi()
    test(comedi_obj)


