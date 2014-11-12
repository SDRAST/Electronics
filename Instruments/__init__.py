"""
Support for commercial lab equipment

This module has laboratory instrument prototypes.  The specific classes are
grouped by manufacturer::
 * Instruments.Agilent (repository Electronics_Instruments_Agilent)
 * Instruments.Valon   (repository Electronics_Interfaces_Valon)

This modules defines generic devices
"""

class PowerMeter(object):
  """
  Class with features common to most power meters.

  Public attributes::
   filter -

  The 'filter' setting defines the number of samples that are averaged together
  with the lowest number typically being for a single reading.
  """
  
  def __init__(self,num_averages={0:1}):
    """
    """
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
  
  def read(self):
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
    pass

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
    pass

  def get_units(self):
    """
    """
    pass
  
=======
import logging

module_logger = logging.getLogger(__name__)

class Synthesizer(object):
  """
  Synthesizer prototype

  It has only one output.  So a more sophisticated device having multiple
  outputs must be subclassed as multiple one-output devices.  Each of these
  must also be subclassed to this superclass.  The helper method
  SynthesizerInstance() is used to provide the correct instance and to make
  sure that there is only one, so that there is no conflict in the device use.
  """
  def __init__(self):
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
>>>>>>> 27548ac0065d1e560f0ecffd50956438dd2a38c5
