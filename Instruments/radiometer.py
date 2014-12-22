"""
module provides class for multi-threaded simultaneous power meter reading
"""
import time
import datetime
import logging
import os
import Queue
from math import log

module_logger = logging.getLogger(__name__)

from Electronics.Instruments import DeviceReadThread
from support.rtc import RTC, Signaller

class Radiometer(object):
  """
  class for multiple power meters reading in synchrony
  """  
  def __init__(self, PM, PMlist, rate=2):
    """
    Create a synchronized multi-channel power meter

    @param PM : dict of power meters
    @type  PM : dict of PowerMeter sub-class objects

    @param PMlist : ordered list of power meter IDs
    @type  PMlist : list of str or list of int
    """
    self.logger = logging.getLogger(module_logger.name+".Radiometer")
    # The following is very specific to the RTC on the Sony Vaio VGN-Z540
    rate_code = int(round(log(rate,2)))
    if 2**rate_code != rate:
      self.logger.warning("Using sampling rate of %d", 2**rate_code)
      self.rate = 2**rate_code
    else:
      self.rate = rate
    #self.rtc = RTC()
    #self.rtc.N_pps.set_rate(rate_code)
    #self.rtc.N_pps.start()
    #self.logger.debug(" RTC.N_pps started")
    #self.sig = Signaller(self.rtc)
    #self.logger.debug(" signaller started")
    signal.signal(signal.SIGALRM, signalHandler)
    self.pm_reader = {}
    self.queue = {}
    for key in PMlist:
      PM[key].name = key
      self.queue[key] = Queue.Queue()
      self.pm_reader[key] = DeviceReadThread(self, PM[key])
      self.pm_reader[key].daemon = True
    self.logger.debug(" initialized")

  def start(self):
    """
    Starts the signaller and the threads
    """
    for key in self.pm_reader.keys():
      self.pm_reader[key].start()
    self.sig.start()
    self.logger.debug(" all started")
    
  def action(self,pm):
    """
    Action performed by thread for power meter

    This action is invoked by the DeviceReadThread object

    @param pm : power meter
    @type  pm : any instance of a PowerMeter class
    """
    #self.sig.signal.wait()
    while True:
      signal.pause()
      reading = pm.power()
      t = time.time()
      self.queue[pm.name].put((t, reading))
    
  def close(self):
    """
    Terminates the signaller, RTC and the power meter reading threads
    """
    self.logger.debug(" stopping")
    for key in self.pm_reader.keys():
      self.pm_reader[key].terminate()
      self.pm_reader[key].join()
    self.sig.terminate()
    self.sig.join()
    self.rtc.close()
