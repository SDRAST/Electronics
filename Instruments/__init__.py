"""
Support for commercial lab equipment

This module has laboratory instrument prototypes.  The specific classes are
grouped by manufacturer::
 * Instruments.Agilent (repository Electronics_Instruments_Agilent)
 * Instruments.Valon   (repository Electronics_Interfaces_Valon)

This modules defines generic devices
"""
import threading
import logging
from MonitorControl import MCobject

module_logger = logging.getLogger(__name__)


class PowerMeter(MCobject):
  """
  Class with features common to most power meters.

  Public attributes::
   filter -

  The 'filter' setting defines the number of samples that are averaged together
  with the lowest number typically being for a single reading.
  """
  
  def __init__(self):
    """
    """
    self.logger = logging.getLogger(module_logger.name+".PowerMeter")
    # Typical defaults attributes; replace in sub-class
    self.f_min =   0 # GHz
    self.f_max =  27 # GHz
    self.p_min = -50 # dBm
    self.p_max =   0 # dBm
    self.units  =  "dBm"
    self.trigmode = "one-shot" # or "free-run" or "trigger"
    self.num_avg = 1
    self._attributes_ = ["f_min", "f_max", "p_min", "p_max",
                         "units", "trigmode", "num_avg"]

  def __dir__(self):
    return self._attributes_

  def _add_attr(self, attr):
    try:
      self._attributes_.index(attr)
    except ValueError:
      self._attributes_.append(attr)

  def __str__(self):
    return self.base()+' "'+str(self.name)+'"'

  def __repr__(self):
    return self.base()+' "'+str(self.name)+'"'

  def base(self):
    """
    String representing the class instance type
    """
    return str(type(self)).split()[-1].strip('>').strip("'").split('.')[-1]

  #  These methods are expected to be replaced by the sub-class
  
  def power(self):
    """
    """
    pass

  def set_trigmode(self, trigcode="one-shot"):
    """
    """
    pass
      

  def get_trigmode(self):
    """
    """
    return self.trigmode

  def set_averaging(self, avg_code=0):
    """
    """
    pass

  def get_averaging(self):
    """
    """
    pass

  def set_units(self, units="dBm"):
    """
    """
    self.units = "dBm"

  def get_units(self):
    """
    """
    return self.units

    
class Synthesizer(MCobject):
  """
  Synthesizer prototype

  It has only one output.  So a more sophisticated device having multiple
  outputs must be subclassed as multiple one-output devices.  Each of these
  must also be subclassed to this superclass.  The helper method
  SynthesizerInstance() is used to provide the correct instance and to make
  sure that there is only one, so that there is no conflict in the device use.
  """
  def __init__(self):
    self.logger = logging.getLogger(module_logger.name+".Synthesizer")
    # These are the minimum attributes of a Synthesizer
    self.__get_tasks__ = {"frequency":  None,
                          "rf_level":   None,
                          "phase lock": None}
    self.__set_tasks__ = {"frequency":  None,
                          "rf_level":   None}
    self.freq = {}
    self.pwr = {}
    self.lock = {}
    raise NotImplementedError(
      "Cannot implement Synthesizer directly. Use SynthesizerInstance.")

  def set_p(self,param, val):
    raise NotImplementedError(
      "This method is not implemented by %s", self.__class__.__name__)

  def get_p(self,param):
    raise NotImplementedError(
      "This method is not implemented by %s", self.__class__.__name__)


class VoltageSource(MCobject):
  """
  Superclass for all voltage source classes

  @ivar volts : output voltage
  @type volts : float
  """
  def __init__(self, name, parent=None):
    """
    Initializes a generic, no hardware voltage source to define attributes.

    This can be used to test software without hardware.
    """
    self.parent = parent
    self.name = name
    self.volts = None
    self.logger = logging.getLogger(module_logger.name+".VoltageSource")

  def getVoltage(self):
    """
    Stub to be replaced by subclass hardware interface
    """
    return self.volts

  def setVoltage(self, volts):
    """
    Stub to be replaced by subclass hardware interface
    """
    self.volts = volts
    return self.get_voltage()


class Attenuator(MCobject):
  """
  Generic attenuator defines basic methods and attributes.

  Can be used for software testing without hardware.
  """
  def __init__(self, parent=None, name=None):
    """
    """
    self.name = name
    self.parent = parent
    self.atten = None

  def get_atten(self):
    """
    """
    return self.atten

  def set_atten(self, atten):
    self.atten = atten
    return self.atten


class DeviceReadThread(threading.Thread):
  """
  One thread in a multi-threaded, multiple device instrument

  This creates a thread which can be started, terminated, suspended, put to
  sleep and resumed. For more discussion see
  http://mail.python.org/pipermail/python-list/2003-December/239268.html
  """

  def __init__(self, parent, device):
    """
    Create a DeviceReadThread object

    @param parent : the object invoking the thread
    @type  parent : some class instance for which an action is defined

    @param device : some instance of a controlable device
    @type  device : object
    """
    mylogger = logging.getLogger(module_logger.name+".DeviceReadThread")
    threading.Thread.__init__(self, target=parent.action)
    self.logger = mylogger
    self.parent = parent
    self.end_flag=False
    self.thread_suspend=False
    self.sleep_time=0.0
    self.thread_sleep=False
    self.device = device
    self.name = device.name
    self.logger.debug(" initialized thread %s", self.name)

  def run(self):
    """
    """
    self.logger.debug("run: thread %s started", self.name)
    while not self.end_flag:
      # Optional sleep
      if self.thread_sleep:
        time.sleep(self._sleeptime)
      # Optional suspend
      while self.thread_suspend:
        time.sleep(1.0)
      self.parent.action(self.device)
    self.logger.info(" thread %s done", self.name)

  def terminate(self):
    """
    Thread termination routine
    """
    self.logger.info(" thread %s ends", self.name)
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
