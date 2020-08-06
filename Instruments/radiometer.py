"""
module provides class for multi-threaded simultaneous power meter reading
"""
import time
import datetime
import logging
import numpy as N
import os
import threading
import signal
from math import log10

module_logger = logging.getLogger(__name__)

from Electronics.Instruments import DeviceReadThread
from local_dirs import log_dir
from support import NamedClass, sync_second

data_path = log_dir+"/Radiometer/"

class Radiometer(NamedClass):
  """
  Class for reading multiple power meters synchronous
  
  The class initiates a system signal with a handler imaginatively called
  'signalHandler()'. An event called 'take_data' which is initially cleared.
  It then starts a reader thread for every power meter.  Each reader has two
  associated events, 'reader_started' and 'reader_done'. Both are initially
  False. A method 'action()' is provided to be invoked by the reader threads.
  When the Radiometer is started, a system timer is intialized with a handler
  called 'update_interval()'. When the timer fires, 'signalHandler()'
  does nothing if 'take_data' is set.  If it is not, then it waits until all
  the readers have completed their 'action()'. It stays in this wait loop
  using time.sleep(). When all the readers are done, it formats an output
  line with the mean time of all the reading times and the readings and writes
  the line to the datafile, flushing the buffer afterwards.
  
  Public Attributes::
    integration     - 2*update_interval for Nyquist sampling
    last_reading    - results of the last power meter reading
    logger          - logging.Logger object
    pm_reader       - DeviceReadThread object
    reader_done     - threading.Event object, set when reading has been taken
    reader_started  - threading.Event object, set when a reading is started
    run             - True if the radiometer is running
    take_data       - threading.Event object to signal readers to take reading
    update_interval - inverse of reading rate
  """  
  def __init__(self, PM, rate=1./60):
    """
    Create a synchronized multi-channel power meter
    
    If the radiometer is started without a rate being given then the default is
    once per minute.

    @param PM : dict of power meters
    @type  PM : dict of PowerMeter sub-class objects
    
    @param rate : number of readings/sec
    @type  rate : float
    """
    self.logger = logging.getLogger(module_logger.name+".Radiometer")
    self.set_rate(rate)
    # create a timer and timer event handler
    signal.signal(signal.SIGALRM, self.signalHandler)
    self.logger.debug("__init__: signal handler assigned")
    self.take_data = threading.Event()
    self.take_data.clear()
    self.logger.debug("__init__: 'take_data' event created and cleared")
    # set power meter averaging
    #    still needs to be done
    # assign reader threads
    self.pm_reader = {}
    self.reader_started = {}
    self.reader_done = {}
    self.last_reading = {}
    for key in list(PM.keys()):
      PM[key].name = key
      # initial reading to wake up Radipower
      self.last_reading[key] = PM[key].power() 
      self.pm_reader[key] = DeviceReadThread(self, PM[key])
      self.logger.debug("__init__: reader and queue %s created", key)
      self.pm_reader[key].daemon = True
      # See ~/Python/Thread/daemon.py before uncommenting this code
      #if self.pm_reader[key].isAlive():
      #self.pm_reader[key].join(1) # this blocks the main thread for one sec
      self.reader_started[key] = threading.Event()
      self.reader_started[key].clear()
      self.reader_done[key] = threading.Event()
      self.reader_done[key].clear()
      self.logger.debug("__init__: 'reader done' event %s created and cleared",
                        key)
    self.logger.debug(" initialized")

  def set_rate(self, rate):
    """
    """
    # set the sampling rate and integration time to Nyquist
    self.update_interval = 1./rate # sec
    self.logger.debug("__init__: interval is %f", self.update_interval)
    self.integration = 2*self.update_interval # Nyquist sampling
  
  def start(self):
    """
    Starts the signaller and the threads
    """
    for key in list(self.pm_reader.keys()):
      self.pm_reader[key].start()
    sync_second()
    signal.setitimer(signal.ITIMER_REAL, self.update_interval, self.update_interval)
    self.logger.debug("start: timer started with %f s interval", self.update_interval)
        
  def signalHandler(self, *args):
    """
    Actions to take when the timer goes off::
      1. Ignore signal if take_data is set
      2. Set take_data
      3. Waits until all readers have started.
      4. Clears take_data.
      5. Waits until all readers have finished.
    It also traps a keyboard interrupt and closes the radiometer
    """
    def check_reader_status(flag, name):
      """
      Checks remaining readers to see if they have finished
      """
      reader_list = list(flag.keys())
      while len(reader_list):
        try:
          for key in reader_list:
            time.sleep(0.001)
            if flag[key].is_set():
              self.logger.debug("signalHandler: %s %d is set", name, key)
              reader_list.remove(key)
            else:
              self.logger.debug("signalHandler: %s %d is not set", name, key)
        except KeyboardInterrupt:
          self.logger.warning("signalHandler.check_reader_status: interrupted")
          self.close()
      return True
      
    def format_time(t):
      isec,fsec = divmod(t,1)
      timestr = time.strftime("%j %H%M%S", time.gmtime(t))
      secfmt = "%."+str(max(0,-int(round(log10(self.update_interval)))+1))+"f"
      self.logger.debug("action.format_time: seconds format: %s", secfmt)
      secstr = (secfmt % fsec)[1:]
      self.logger.debug("action.format_time: seconds str: %s", secstr)
      return timestr+secstr
      
    if self.take_data.is_set():
      self.logger.warning("signalHandler is busy and skipped")
    else:
      self.logger.debug("signalHandler: called")
      try:
        self.logger.debug("signalHandler: setting take_data")
        self.take_data.set() # OK to take data
        # wait until all the readers have started
        if check_reader_status(self.reader_started, "reader_started is set"):
          self.take_data.clear()
        self.logger.debug("signalHandler: take_data is cleared")
        # wait until all the readers are done
        if check_reader_status(self.reader_done, "reader_done"):
          self.logger.debug("signalHandler: all readers done")
      except KeyboardInterrupt:
        self.logger.warning("signalHandler: interrupted")
        self.close()
      except Exception as details:
        self.logger.warning("signalHandler: %s", details)
      # output data array
      ar = N.array(list(self.last_reading.values()))
      t = ar[:,0].mean()
      powers = tuple(ar[:,1])
      try:
        outstr = format_time(t) + (8*" %6.2f" % powers)
      except TypeError as details:
        self.logger.warning("signalHandler: conversion failed: %s", details)
        outstr = format_time(t) + ("%s" % powers)
      try:
        self.datafile.write(outstr+"\n")
        self.datafile.flush()
      except Exception:
        pass
  
  #def running(self):
  #  return self.run
    
  def action(self, pm):
    """
    Action performed by thread for power meter

    Actions invoked by the DeviceReadThread object::
      1. Wait until take_data is set.
      2. Sets reader_started event.
      3. Takes a power meter reading.
      4. Clears reader_started event.
      5. Saves reading in last_reading.
      6. Sets reader_done.

    @param pm : power meter
    @type  pm : any instance of a PowerMeter class
    """
    try:
      self.logger.debug("action: %s waiting for signal", pm.name)
      self.take_data.wait()
      self.reader_started[pm.name].set()
      self.logger.debug("action: %s reader started", pm.name)
      reading = pm.power()
      self.logger.debug("action: reading %s completed", pm.name)
      self.reader_started[pm.name].clear()
    except KeyboardInterrupt:
      self.close()
    t = time.time()
    self.last_reading[pm.name] = (t, reading)
    self.reader_done[pm.name].set()
  
  def get_readings(self):
    """
    Returns results of ongoing or just completed reading.
    """
    while self.take_data.is_set():
      time.sleep(0.001)
    return self.last_reading
    
  def close(self):
    """
    Terminates the signaller, RTC and the power meter reading threads
    """
    signal.setitimer(signal.ITIMER_REAL, 0)
    self.logger.debug("close: stopping")
    self.take_data.clear()
    for key in list(self.pm_reader.keys()):
      self.pm_reader[key].terminate()
      self.logger.debug("close: reader %d terminated", key)
    self.run = False
