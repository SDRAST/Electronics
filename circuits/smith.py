"""
Smith chart functions

support for impedance matching using a Smith Chart
"""
import logging
from math import atan2, cos, degrees, pi, sin, tan

from Electronics.circuits.filters import reactance_to_component, Xcap, Xind
import Math.geometry as G

logger = logging.getLogger(__name__)

def reflec_coef(ZL, Z0=50+0j):
  """
  reflection coefficient (Gamma)
  
  Args
  ====
  ZL - (complex) load impedance
  Z0 - (complex) source impedance
  """
  return (ZL-Z0)/(ZL+Z0)

def norm_admittance(gamma):
  """
  reflection coefficient to normalized admittance
  """
  return (1-gamma)/(1+gamma)

def norm_impedance(gamma):
  """
  reflection coefficient to normalized impedance
  """
  return (1+gamma)/(1-gamma)

def admittance(gamma, Z0):
  return norm_admittance(gamma)/Z0
  
def impedance(gamma, Z0):
  return Z0*norm_impedance(gamma)

def load_circles(gamma):
  """
  return location and radius of constant r (or g) circles through the load
  
  A circle is labeled `"g"` if `gamma` is not inside the r=1 circle, and `"r"`
  if it is not in the g=1 circle. `gamma` outside these circles will have two
  circles, labeled `"g"` and `"r"`.
  
  Args
  ====
  posL - (complex) position of the load in the Gamma plane
  
  Returns
  =======
  dict - keyed with "r" and/or "g" and the circle center and radius
  """
  def compute_circle(center, gamma):
    """
    Args
    ====
    center - (real) +1 for `r` or -1 for `b`
    """
    if abs(center) != 1:
      logger.error("load_circle: compute_circle: center=%s not allowed", center)
      return None
    line_ctr = ((center+0j) + gamma)/2
    line = gamma - (center+0j)
    linecos = line.real
    linesin = line.imag
    slope = linesin/linecos
    angle = atan2(linesin, linecos)
    logger.debug("load_circle: compute_circle: "+
                 "center from (%d+0j) at %s with line slope %6.2f (%5.1f deg)",
                 center, line_ctr, slope, degrees(angle))
    circle_ctr = complex(line_ctr.real + line_ctr.imag*tan(angle), 0)
    circle_radius = 1-abs(circle_ctr.real)
    logger.debug("load_circle: compute_circle: "+
                 "center at %s with radius %4.2f",
                 circle_ctr, circle_radius)
    return circle_ctr, circle_radius
  
  result = {"R load": gamma}
  yL = norm_admittance(gamma)
  print("compute_circle: yL =", yL)
  gL,bL = yL.real, yL.imag
  zL = norm_impedance(gamma)
  print("compute_circle: zL =", zL)
  rL,xL = zL.real, zL.imag
  if abs(gamma - (+0.5+0j)) <= 0.5:
    # inside the r=1 circle; need constant g circle
    result["g"] = {"circle": compute_circle(-1, gamma)}
  elif abs(gamma - (-0.5+0j)) <= 0.5:
    # inside the g=1 circle; need constant r circle
    result["r"] = {"circle": compute_circle(+1, gamma)}
  else:
    # both constant x and b circles can be used
    result["g"] = {"circle": compute_circle(-1, gamma)}
    result["r"] = {"circle": compute_circle(+1, gamma)}
  return result
  
def matching_network(ZL, f, Z0=50, plot=False):
  """
  Solves for L-circuit matching networks using the Smith chart
  
  Args
  ====
    ZL - (complex) load impedance in ohms
    f  - (float) frequency in Hz
    Z0 - (float) input or transmission line impedance in ohms
  
  Returns
  =======
  A list with a string for the circuit type, and solution tuples consisting of
  two component tuples with a value and a unit.  
  
  Notes
  =====
  If the load circle is type `"r"` then the path to follow is a constant `b`
  curve and the circuit will be type "fu".  If the load circle is type `"r"` 
  then the path to follow is a constant `b` curve and the circuit will be type
  "gamma".
  
  The circuit type is "gamma" if the first component is in series with the load
  and the second component in parallel to those two. (The circuit looks like a
  Greek capital Gamma.)  The circuit type is "fu" if the first component is
  parallel to the load, and the second component feeds that pair. (The circuit
  looks like a Katakana Hu, pronounced "fu".)
  """
  netdata = {}
  zL = ZL/Z0
  logger.info("matching_network: ZL=%s, zL=%s, Z0=%s, %8.2e", ZL,zL, Z0, f)
  netdata['load z'] = zL
  gamma = reflec_coef(zL, Z0=1)
  logger.info("matching_network: gamma = %s", gamma)  
  yL = 1/zL
  logger.debug("matching_network: norm. admittance, yL = %s", yL)
  
  # compute constant load circle center and radius
  LCs = load_circles(gamma)
  logger.debug("matching_network: LCs: %s", LCs)
  for key in LCs.keys():
    netdata[key] = LCs[key]
    if key == "R load":
      continue
    circle_ctr, circle_radius = LCs[key]["circle"]
    const_circle = G.Circle(circle_radius, center=(circle_ctr.real, 0))
    if key == "r": # circle through load is constant `r`
      # find the intersection with the y=1+ib circle
      intersects = const_circle.intersect(G.Circle(0.5, center=(-0.5, 0)))
    elif key == "g": # circle through load is constant `g`
      # find the intersection with the z=1+ix circle
      intersects = const_circle.intersect(G.Circle(0.5, center=( 0.5, 0)))
    netdata[key]['intersects'] = intersects
    logger.debug("matching_network: intersects at gamma = %s", intersects)
    for intersect in intersects:
      index = intersects.index(intersect)
      netdata[key][index] = {}
      gammaX = complex(*(intersect))
      admitX = norm_admittance(gammaX)
      logger.debug("matching_network: intersect at y = %s", admitX)
      impedX = norm_impedance(gammaX)
      logger.debug("matching_network: intersect at y = %s", impedX)
      
      # impedance or admittance of the intersection
      if key == "g":
        # load is on a `g=1` circle 
        # a move to a specific intersection has the opposite sign in `z`-space
        # and `y`-space
        netdata[key][index]['y'] = admitX
        b = admitX.imag
        delta_b = -(b - yL.imag) # yL is the load susceptance
        logger.debug("additional norm. susceptance: %8.3f", delta_b)
        netdata[key][index]['Delta b'] = -delta_b
        # this is a "fu" circuit; component in parallel with load
        # shift is delta_b
        Zpar = reactance_to_component(Z0/delta_b, f)
        netdata[key][index]['par'] = Zpar
        # we need to remove the remaining reactance
        x = -impedX.imag
        logger.debug(
               "matching_network: remaining reactance or susceptance: %8.3f", x)
        netdata[key][index]['Delta x'] = -x
        # this is a "fu" circuit; shift is delta_x
        Zser = reactance_to_component(Z0*x, f)
        netdata[key][index]['ser'] = Zser
      elif key == "r":
        # load is on an `r=1` circle
        netdata[key][index]['z'] = impedX
        x = impedX.imag
        delta_x =   x - zL.imag # zL is the load reactance
        logger.debug("additional norm. reactance: %8.3f", delta_x)
        netdata[key][index]['Delta x'] = delta_x
        # this is a "gamma" circuit; component in series with load
        # shift is delta_x
        Zser = reactance_to_component(Z0*delta_x, f)
        netdata[key][index]['ser'] = Zser
        # we need to remove the remaining reactance
        b = admitX.imag
        logger.debug(
                 "matching_network: remaining reactance or reactance: %8.3f", b)
        netdata[key][index]['Delta b'] = b
        # this is a gamma circuit; shift is delta_b
        Zpar = reactance_to_component(Z0/b, f)
        netdata[key][index]['par'] = Zpar
      else:
        logger.error("matching_network: invalid key: %s", key)
        continue      
  return netdata

def matched_impedance(ZL, circ_type, parallel, series, f):
  """
  Args
  ====
  ZL        - (complex) load impedance
  circ_type - (str) "r" for gamma network, "g" for fu network
  parallel  - (float, str) reactance of parallel component
  series    - (float, str) reactance of series component
  f         - (float or nparray) frequencies
  """
  if parallel[1] == "H":
            Xpar = Xind(parallel[0], f)
  else:
            Xpar = Xcap(parallel[0], f)
  if series[1] == "H":
            Xser = Xind(series[0], f)
  else:
            Xser = Xcap(series[0], f)
  # check matched impedance
  if circ_type == "g":   # 
            Ztot = 1/(1/ZL + 1/Xpar) + Xser
  elif circ_type == 'r': # gamma circuit
            Ztot = 1/(1/Xpar + 1/(ZL+Xser))
  else:
            logger.error("matching_network: invalid key (6): %s", circ_type)
            Ztot = None
  return Ztot

