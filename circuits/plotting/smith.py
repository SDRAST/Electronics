"""
plots Smith charts

The functions here plot on the standard Smith chart, but the argument
`admittance=True` will plot on the inverse Smith chart

Notes
=====

  Z = R + iX;  Y = 1/Z = G + iB
  Z: impedance    R: resistance    X: reactance
  Y: admittance   G: conductance   B: susceptance
"""

from pylab import *

from .. import component_text
from Electronics.circuits.filters import (Xcap, Xind, Z_lopass, Z_hipass, 
                                          Z_bandpass)
from ..smith import reflec_coef
  
def circle(center=(0,0), radius=1):
  """
  returns 360 (x,y) points of a circle
  """
  if type(center) == complex:
    center = center.real, center.imag
  theta = linspace(0, 2*pi, 360)
  x = center[0] + radius*cos(theta)
  y = center[1] + radius*sin(theta)
  return x,y
  
def points(Z, Z0=50+0j, marker='o', linestyle="", color=None,
           label="", admittance=False):
  """
  plots (x,y) reflection coefficient points given by impedance Z
  
  If admittance is True, then Z is reall Y and it plots 1/Y.
  
  The default is to plot points using default colors
  
  Args
  ====
    Z          - (complex) NP array of impedance points to be plotted
    Z0         - (complex) input or line impedance
    label      - (str) string for the legend
    admittance - (bool) plots admittance instead of impedance if True
  """
  if admittance:
    # then Z is really Y
    gamma = reflec_coef(1/Z, Z0=1/Z0)
  else:
    gamma = reflec_coef(Z, Z0=Z0)
  plotted = plot(gamma.real, gamma.imag, marker=marker, color=color,
                 ls=linestyle, label=label)
  return plotted

def plot_constant_X(X, Z0=50+0j, admittance=False, R=linspace(1,1000,100),
                    linestyle=":", color="k", marker=None, mirror=False):
  """
  plots a reactance `X` (or susceptance `B`) line over a range of `R`
  """
  points(R+X*1j, Z0=Z0, color=color, linestyle=linestyle, marker=marker,
         admittance=admittance)
  if mirror:
    points(R-X*1j, Z0=Z0, color=color, linestyle=linestyle, marker=marker,
           admittance=admittance)
  if admittance:
    txt = r"$1/%.1f\Omega$" % X
    R = reflec_coef(1/( X*1j), Z0=1/Z0)
    text(R.real, R.imag,     txt, va="top", color=color)
    if mirror:
      R = reflec_coef(1/(-X*1j), Z0=1/Z0)
      text(R.real, R.imag, "-"+txt, va="top", color=color)
  else:
    txt = r"$%.1f\Omega$" % X
    R = reflec_coef( X*1j, Z0=Z0); text(R.real, R.imag,     txt, va="bottom",
                    color=color)
    if mirror:
      R = reflec_coef(-X*1j, Z0=Z0); text(R.real, R.imag, "-"+txt, va="bottom",
                      color=color)

def plot_constant_R(R, Z0=50+0j, admittance=False, mirror=False,
                    color=None, marker=None, linestyle='-',
                    X = array([0.1, 1, 5, 10, 20, 35, 50, 70, 100, 150, 200,
                               300, 500, 1e3, 1e6]) ):
  """
  plots a resistance `R` (or conductance `G`) line over a range of `X`.
  
  The default `X` goes from almost 1+0j (or -1+0j) to almost the perimeter.
  
  Notes
  =====
  Plotting is done by `points()` which converts Z to gamma assuming Z0. 
  If `admittance` is True, then R -> 1/R and Z0 -> 1/Z0.  For this reason,
  if you have b (= 1/r = Z0/R) then Z0 is really Y0 and so the arguments are
  (b*Z0, Z0).
  
  Args
  ====
    R          - (real) un-normalized resistance; if normalized, set Z0=1
    Z0         - (real) characteristic (input or line) impedance
    admittance - (bool) if true, R is actually G
    mirror     - (bool) if true, both R and -R are plotted
    color      - (str) line or marker color
    marker     - (str) symbol to plot
    linestyle  - (str) for lines connecting data points
    X          - (list of real) points to for Z=R+iX points to plot
  """
  if type(X) == list:
    X = array(X)
  if admittance:
    txt = r"$R=1/"+str(R)+"\Omega$"
    p = points(R+X*1j, Z0=Z0, color=color, linestyle=linestyle, marker=marker,
               admittance=admittance)
  else:
    txt = r"$R="+str(R)+"\Omega$"
    p = points(R+X*1j, Z0=Z0, color=color, linestyle=linestyle, marker=marker,
               label=txt, admittance=admittance)
  if mirror:
    if admittance:
      pass
    else:
      color = p[-1].get_color()
    points(R-X*1j, color=color, linestyle=linestyle, marker=marker,
           admittance=admittance)

def init_smith(size=(8,8), plottitle=""):
  """
  initilaize a Smith chart
  """
  figure(figsize=size)
  x,y = circle()
  plot(x,y,'k-')
  plot([-1,1],[0,0],'k')
  title(plottitle)

def gamma_arrow(Rload, RX, color="k", txt="", ha='center'):
  """
  Args
  ====
  Rload - (complex) reflection coefficient (Gamma) of load
  RX    - (complex) reflection coefficient (Gamma) of intersection
  """
  x0,y0 = Rload.real, Rload.imag
  dx, dy = RX.real-x0, RX.imag-y0
  arrow(x0,y0, dx,dy, width=.005, head_length=0.05, head_width=0.02,
                      length_includes_head=True, color=color)
  if txt:
    text(x0+dx/2, y0+dy/2, txt, ha=ha, color=color)
      
def plot_solutions(netdata, Z0=50, plottitle=None):
  """
  Plots the results returned from `matching_network()`.
  """
  have_plot=False
  if have_plot:
    pass
  else:
    load_z = netdata['load z']
    load_r = netdata['load z'].real
    load_x = netdata['load z'].imag
    load_y = 1/netdata['load z']
    load_g = load_y.real
    load_b = load_y.imag
    if plottitle:
      init_smith(plottitle=plottitle)
    else:
      init_smith(plottitle="z="+str(load_z))
    have_plot=True
  
  # plot load
  plot(netdata['R load'].real, netdata['R load'].imag,'o')
  
  
  for circ_type in ['r', 'g']:
    if circ_type in netdata.keys():
      # plot intersection points
      for R,I in netdata[circ_type]['intersects']:
        plot(R,I,'o')
        center, radius = netdata[circ_type]['circle']
        x,y = circle(center=center, radius=radius)
        plot(x,y, circ_type+"--")
  
      # plot target circle
      if circ_type == "g":
        center, radius = 0.5+0j, 0.5
      elif circ_type == "r":
        center, radius = -0.5+0j, 0.5
      else:
        print("no load resistance/conductance circle")
      x,y = circle(center=center, radius=radius)
      plot(x,y,"k:")
  
      # plot reactance/susceptance curves
      for idx in [0,1]:
        solution = netdata[circ_type][idx]
        if 'z' in solution:
          z = solution['z']
          x = z.imag
          plot_constant_X(Z0*x, Z0=Z0)
          plot_constant_X(load_x*Z0, Z0=Z0, mirror=False)
          # from load point to intercept points
          gamma_arrow(reflec_coef(load_z, Z0=1), reflec_coef(z, Z0=1), 
                      color=circ_type,
                      txt=component_text(solution['ser'])+" ", ha="right")
          gamma_arrow(reflec_coef(z, Z0=1), (0+0j),
                      txt=component_text(solution['par'])+" ", ha="right")
        elif 'y' in solution:
          y = solution['y']
          b = y.imag
          plot_constant_X(b*Z0, Z0=Z0, admittance=True)
          plot_constant_X(load_b*Z0, Z0=Z0, admittance=True)
          # from load point to intercept points
          gamma_arrow(reflec_coef(1/load_y, Z0=1), reflec_coef(1/y, Z0=1),
                      color=circ_type,
                      txt=" "+component_text(solution['par']), ha="left")
          gamma_arrow(reflec_coef(1/y, Z0=1), (0+0j),
                      txt=" "+component_text(solution['ser']), ha="left")
        else:
          print('No "z" or "y" found')

