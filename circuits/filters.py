"""
computes responses of filters in book Filters section
"""
import logging
from numpy import abs, angle, arctan2, imag, pi, real, sqrt

logger = logging.getLogger(__name__)

def Xcap(C, f):
  """
  reactance of capacitor
  
  blocks low frequencies; high capacitance, less blockage
  
  Args
  ====
  C (float) capacitance in F
  f (float) frequency in Hz
  
  Returns
  =======
  (complex)
  """
  nu = 2*pi*f
  return 0-1j/(nu*C)

def Xind(L, f):
  """
  reactance of inductor
  
  Args
  ====
  f (float) frequency in Hz
  L (float) inductance in H
  
  Returns
  =======
  (complex)
  """
  nu = 2*pi*f
  return 0+1j*nu*L

def Z_low(L, R_L, f):
  """
  impedance in load branch
  
  inductor and load in series
  """
  return Xind(L,f) + R_L 

def Z_high(C, R_L, f):
  """
  impedance in load branch
  
  capacitor and load in series; low frequencies blocked
  """
  return Xcap(C,f) + R_L 

def Z_lopass(C, L, R_L, f):
  """
  extra lowpass with a shunt capacitance for high frequencies
  
  capacitor in parallel with (inductor+load)
  """
  return 1/(1/Xcap(C,f) + 1/Z_low(L, R_L, f))
  
def Z_hipass(C, L, R_L, f):
  """
  extra high pass with shunt inductor for low frequencies
  
  inductor and capacitor+load in parallel; low frequencies shorted
  """
  return 1/(1/Xind(L,f) + 1/Z_high(C, R_L, f))
  
def Z_bandpass(C, L, R_L, f):
  """
  impedance of circuit
  
  capacitor and inductor+load in parallel
  """
  return 1/(1/Xind(L, f) + 1/Xcap(C, f) + 1/R_L)

def V_lopass(V, R_S, C, L, R_L, f):
  """
  lowpass filter's output voltage
  
  current through the load times the load impedance
  """
  # current in circuit
  I = V/(R_S + Z_lopass(C, L, R_L, f))
  # voltage across circuit
  V_out = V - I*R_S
  I_C = V_out/Xcap(C, f)
  I_L = V_out/Z_low(L, R_L, f)
  V_L = I_L*R_L
  return V_L

def V_hipass(V, R_S, C, L, R_L, f):
  """
  filter output voltage
  
  current through the load times the load impedance
  """
  # current in circuit
  I = V/(R_S + Z_hipass(C, L, R_L, f))
  # voltage across circuit
  V_out = V - I*R_S
  I_L = V_out/Z_high(C, R_L, f) # current through load branch
  V_L = I_L*R_L # voltage across load
  return V_L

def V_bandpass(V, R_S, C, L, R_L, f):
  """
  filter output voltage
  
  input voltage minus the current times the source impedance
  """
  # current in circuit
  I = V/(R_S + Z_bandpass(C, L, R_L, f))
  # voltage across circuit
  V_out = V - I*R_S
  return V_out

def reactance_to_component(reactance, freq):
  """
    Based on X = 1/(2 pi f C), and X = 2 pi f L,
    so       C = 1/(2 pi f X), and L = X/(2 pi f)
  """
  logger.debug("reactance_to_component: reactance= %8.3f", reactance)
  factor = 2*pi*freq
  if reactance < 0:
    # compute capacitance
    return -1/(factor*reactance), "F"
  else:
    # compute inductance
    return reactance/factor, "H"

