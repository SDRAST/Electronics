"""
module provides class for multi-threaded simultaneous power meter reading
"""
import time
import datetime
import logging
import os
import threading
#import Queue
import signal
from math import log

module_logger = logging.getLogger(__name__)

from Electronics.Instruments import DeviceReadThread
from support import sync_second

data_path = "/tmp/"

class Radiometer(object):
  """
  class for multiple power meters reading in synchrony
  """  
  def __init__(self, PM, rate=0.2):
    """
    Create a synchronized multi-channel power meter
    
    

    @param PM : dict of power meters
    @type  PM : dict of PowerMeter sub-class objects
    
    @param rate : number of samples/sec
    @type  rate : float
    """
    self.logger = logging.getLogger(module_logger.name+".Radiometer")
    # set the sampling rate and integration time to Nyquist
    self.update_interval = 1./rate # sec
    self.logger.debug("__init__: interval is %f", self.update_interval)
    self.integration = 2*self.update_interval
    # create a timer and timer event handler
    signal.signal(signal.SIGALRM, self.signalHandler)
    self.logger.debug("__init__: signal handler assigned")
    self.take_data = threading.Event()
    self.take_data.clear()
    self.logger.debug("__init__: 'take_data' event created and cleared")
    # set power meter averaging and assign reader threads
    self.pm_reader = {}
    #self.queue = {}
    self.datafile = {}
    self.reader_started = {}
    self.reader_done = {}
    self.last_reading = {}
    for key in PM.keys():
      PM[key].name = key
      PM[key].set_averaging(self.integration*100)
      #self.queue[key] = Queue.Queue()
      self.datafile[key] = open(data_path
                               +datetime.datetime.now().strftime(
                                               "PM%Y%j-%H%M%S-"+str(key)), "w")
      self.pm_reader[key] = DeviceReadThread(self, PM[key])
      self.logger.debug("__init__: reader and queue %s created", key)
      self.pm_reader[key].daemon = True
      if self.pm_reader[key].isAlive():
        self.pm_reader[key].join(1)
      self.reader_started[key] = threading.Event()
      self.reader_started[key].clear()
      self.reader_done[key] = threading.Event()
      self.reader_done[key].clear()
      self.logger.debug("__init__: 'reader done' event %s created and cleared",
                        key)
    self.logger.debug(" initialized")

  def signalHandler(self, *args):
    """
    """
    def check_reader_status(flag, name):
      """
      """
      reader_list = flag.keys()
      while len(reader_list):
        for key in reader_list:
          time.sleep(0.001)
          if flag[key].is_set():
            self.logger.info("signalHandler: %s %d is set", name, key)
            reader_list.remove(key)
          else:
            self.logger.info("signalHandler: %s %d is not set", name, key)
      return True
      
    if self.take_data.is_set():
      self.logger.warning("signalHandler is busy and skipped")
    else:
      self.logger.info("signalHandler: called")
      try:
        self.logger.info("signalHandler: setting take_data")
        self.take_data.set() # OK to take data
        # wait until all the readers have started
        if check_reader_status(self.reader_started, "reader_started is set"):
          self.take_data.clear()
        self.logger.info("signalHandler: take_data is cleared")
        # wait until all the readers are done
        if check_reader_status(self.reader_done, "reader_done"):
          self.logger.info("signalHandler: all readers done")
      except KeyboardInterrupt:
        self.logger.warning("signalHandler: interrupted")
        self.close()
      except Exception, details:
        self.logger.warning("signalHandler: %s", details)
  
  def start(self):
    """
    Starts the signaller and the threads
    """
    for key in self.pm_reader.keys():
      self.pm_reader[key].start()
    sync_second()
    signal.setitimer(signal.ITIMER_REAL, self.update_interval, self.update_interval)
    self.logger.debug("start: timer started with %f s interval", self.update_interval)
    
  def action(self, pm):
    """
    Action performed by thread for power meter

    This action is invoked by the DeviceReadThread object

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
    self.last_reading[pm] = (t, reading)
    #self.queue[pm.name].put((t, reading))
    dt = datetime.datetime.fromtimestamp(t)
    lineout = str(dt)+"\t"+str(reading)+'\n'
    self.datafile[pm.name].write(lineout)
    self.datafile[pm.name].flush()
    self.logger.debug("action: %s put %6.2f in file", pm.name, reading)
    self.reader_done[pm.name].set()
  
  def get_readings(self):
    """
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
    for key in self.pm_reader.keys():
      self.pm_reader[key].terminate()
      self.logger.debug("close: reader %d terminated", key)

