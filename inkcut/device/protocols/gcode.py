# -*- coding: utf-8 -*-
"""
Created on Dec 30, 2016

@author: jrm
"""
from inkcut.device.plugin import DeviceProtocol, Model
from inkcut.core.utils import log, async_sleep
from atom.api import Bool, Instance, Range, Int
from twisted.internet import defer

class GCodeConfig(Model):
    # set to 0 for no timeout (mandatory for slow movement)
    g_code_rx_timeout = Range(low=0,high=20,value=20).tag(config=True)
    # Be sure than your printer firmware is configured with more or equal number of buffering frames
    device_buffer_size = Range(low=1,high=20,value=10).tag(config=True)
    laser_mode = Bool(False).tag(config=True)
    laser_power = Range(low=0,high=100,value=10).tag(config=True)
    working_speed = Range(low=60,high=6000,value=600).tag(config=True)
    travel_speed = Range(low=60,high=6000,value=600).tag(config=True)

class GCodeProtocol(DeviceProtocol):

    config    = Instance(GCodeConfig, ()).tag(config=True)
    g_code_ok = Int()

    def connection_made(self):
        self.g_code_ok = self.config.device_buffer_size
        #wait 10 sec that the printer initialize itself
        #TODO: don't work
        #yield async_sleep(10000)

    def move(self, x, y, z, laser=False, absolute=True):
        if self.config.laser_mode and laser:
            self.write("G0 X%.4f Y%.4f S%i F%i\n" % ( x, y, (self.config.laser_power*0.01)*255, self.config.working_speed))
        else:
            self.write("G0%.2f X%.2f Y%.2f F%i\n" % (z, x, y, self.config.travel_speed))
        self.g_code_ok -= 1
        return self.wait_response()

    @defer.inlineCallbacks
    def wait_response(self):
        timeout = 0
        timeout_limit = self.config.g_code_rx_timeout
        while self.g_code_ok == 0:
            #print("timeout  = ",timeout," gcode = ",self.g_code_ok)
            if timeout_limit:
                timeout += 1
                if timeout >= timeout_limit*10:
                    return
            yield async_sleep(100)
        return

    def set_force(self, f):
        raise NotImplementedError

    def set_velocity(self, v):
        raise NotImplementedError

    def set_pen(self, p):
        raise NotImplementedError

    @defer.inlineCallbacks
    def finish(self):
        timeout = 0
        timeout_limit = self.config.g_code_rx_timeout

        yield self.wait_response()
        self.write("G28 X Y; Return to home\n")
        self.g_code_ok -= 1
        if self.config.laser_mode:
            yield self.wait_response()
            self.write("M3 O0; Laser Off\n")
            self.g_code_ok -= 1

        while self.g_code_ok != self.config.device_buffer_size:
            if timeout_limit:
                timeout += 1
                if timeout >= timeout_limit*10:
                    return
            yield async_sleep(100)

    def data_received(self, data):
        """ Called when the device replies back with data. This can occur
        at any time as communication is asynchronous. The protocol should
        handle as needed.

        Parameters
        ----------
        data


        """
        log.debug("data received: {}".format(data))
        if b'ok' in data:
            self.g_code_ok += data.count(b'ok')

    def connection_lost(self):
        self.g_code_ok = 0
        pass
