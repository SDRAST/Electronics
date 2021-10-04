"""
support for circuit modeling
"""
import logging
from math import floor, log10

logger = logging.getLogger(__name__)

def component_text(component):
  """
  returns a text string for the component
  
  Args
  ====
  component - (float, str) reactance value and unit ('F' or 'H')
  """
  multipliers = {-15: "f", -12: "p", -9: "n", -6: "u", -3: "m", 0: ""}
  value = component[0]
  unit = component[1]
  expon = floor(log10(value))
  if expon < -15:
    display = value/10**(expon-mul)
    return str(display)+"f"+unit
  for mul in multipliers.keys():
    #print("testing expon=",expon,"against multiplier",mul)
    if mul == expon:
      #print("exact match")
      # exact match
      display = value/10**mul
      return str(round(display,2))+multipliers[mul]+unit
    elif expon < mul:
      #print(expon,"<",mul)
      # passed highest multiplier less than exponent
      display = value/10**(mul-3)
      return str(round(display,2))+multipliers[mul-3]+unit
    elif expon > mul:
      continue
    else:
      # must have passed  zero
      return str(value)+unit

