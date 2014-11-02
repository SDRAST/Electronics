"""
Support for commercial lab equipment

This module has laboratory instrument prototypes.  The specific claaes are
grouped by manufacturer:
* Instruments.Agilent (repository Electronics_Instruments_Agilent)
* Instruments.Valon   (repository Electronics_Interfaces_Valon)
"""
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
