"""
module provides class for multi-threaded simultaneous power meter reading
"""
import threading
import time
import datetime
import logging

logging.basicConfig(level=logging.WARNING)
module_logger = logging.getLogger(__name__)

class PMreadThread(threading.Thread):
  """
  One thread in a multi-threaded, multiple PM radiometer
  
  This creates a thread which can be started, terminated, suspended, put to
  sleep and resumed. For more discussion see
  http://mail.python.org/pipermail/python-list/2003-December/239268.html
  """

  def __init__(self, pm):
    """
    Create a PMreadThread object

    @param pm : power meter
    @type  pm : PowerMeter subclass instance
    """
    threading.Thread.__init__(self, target=self.target_func)
    self.end_flag=False
    self.thread_suspend=False
    self.sleep_time=0.0
    self.thread_sleep=False
    self.pm = pm
    self.name = pm.name

  def run(self):
    """
    """
    while not self.end_flag:
      # Optional sleep
      if self.thread_sleep:
        time.sleep(self._sleeptime)
      # Optional suspend
      while self.thread_suspend:
        time.sleep(1.0)
      self.target_func()
    print self.name,"done"

  def target_func(self):
    """
    """
    try:
      time.sleep(1)
      reading = self.pm.read()
      t = datetime.datetime.now()
    except KeyboardInterrupt:
      self.terminate()
      terminate_all()
    timestr = str(t)
    module_logger.info("%s: %s at %s", self.name, reading, timestr)

  def terminate(self):
    """
    Thread termination routine
    """
    print self.name,"ends"
    self.end_flag = True

  def set_sleep(self, sleeptime):
    """
    """
    self.thread_sleep = True
    self._sleeptime = sleeptime

  def suspend_thread(self):
    """
    """
    self.thread_suspend=True

  def resume_thread(self):
    """
    """
    self.thread_suspend=False

class Radiometer(object):
  """
  class for multiple power meters reading in synchrony
  """
  def __init__(self, PMclass, PMlist):
    """
    """
    pm_reader = {}
    for name in PMlist:
      pm = PMclass(name)
      self.pm_reader[name] = PMreadThread(pm)
      self.pm_reader[name].start()
    
  def close():
    """
    """
    for name in self.pm_reader.keys():
      self.pm_reader[name].terminate()
      self.pm_reader[name].join()

if __name__ == "__main__":
  """
  This is a test using HP power meters at Goldstone
  """
  from Electronics.Instruments.Agilent import PM
  mylogger = logging.getLogger()
  mylogger.setLevel(logging.INFO)

  pm_list = ["pm 13-1", "pm 13-4", "pm 13-5", "pm 14-1"] # , "pm 14-2"
  mylogger.info("Starting pm_reader %s at %s", name,
                str(datetime.datetime.now()))
  radiometer = Radiometer(PM, pm_list)
  run = True
  try:
    while run:
      time.sleep(0.1)
  except KeyboardInterrupt:
    run = False

