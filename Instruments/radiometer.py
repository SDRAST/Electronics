"""
module provides class for multi-threaded simultaneous power meter reading
"""
import time
import datetime
import logging
import os

module_logger = logging.getLogger(__name__)

from Electronics.Instruments import DeviceReadThread
from support.rtc import RTC, Signaller

class Radiometer(object):
  """
  class for multiple power meters reading in synchrony
  """  
  def __init__(self, PM, PMlist):
    """
    Create a synchronized multi-channel power meter

    @param PM : dict of power meters
    @type  PM : dict of PowerMeter sub-class objects

    @param PMlist : ordered list of power meter IDs
    @type  PMlist : list of str or list of int
    """
    self.logger = logging.getLogger(module_logger.name+".Radiometer")
    self.rtc = RTC()
    if self.rtc.N_pps.start(1):
      self.logger.debug(" RTC.N_pps started")
    self.sig = Signaller(self.rtc)
    self.sig.start()
    self.logger.debug(" signaller started")
    self.pm_reader = {}
    for key in PMlist:
      self.pm_reader[key] = DeviceReadThread(self, PM[key])
      self.pm_reader[key].daemon = True
      self.pm_reader[key].start()
    self.logger.debug(" started")
  
  def action(self,pm):
    """
    """
    self.logger.debug(" waiting for signal")
    self.sig.signal.wait()
    self.logger.debug(" reading")
    reading = pm.power()
    t = datetime.datetime.now()
    timestr = str(t)[-15:]
    self.logger.info(" %s: %6.2f at %s",pm.name, reading, timestr)
    
  def close(self):
    """
    """
    self.logger.debug(" stopping")
    for key in self.pm_reader.keys():
      self.pm_reader[key].terminate()
      self.pm_reader[key].join()
    self.sig.terminate()