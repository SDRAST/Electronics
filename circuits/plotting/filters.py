"""
Plots output analytic voltage and input impedance of filters

Amplitude and phase are plotted separately, left and right
"""
from pylab import *
from matplotlib.ticker import NullFormatter, ScalarFormatter

from ..filters import V_lopass, V_bandpass, V_hipass

Cmin=1e-20; Cmax=1e+20; Lmin=1e-20; Lmax=1e+20

def plot_filter(V, R_S, C, L, R_L, f, V_filt, Z_filt):
  """
  plots the voltage response and input impedance of filters in module 'filters'
  
  Also plots limiting cases of capacitor only, inductor only, and no filtering.
  
  This handles all plots as if they were to appear in one figure with two rows
  and two columns, but actually puts each row in a different figure.
  """
  fig1, ax1 = subplots(nrows=1, ncols=2, figsize=(10,4))
  fig2, ax2 = subplots(nrows=1, ncols=2, figsize=(10,4))
  ax = append(ax1.reshape(1,2), ax2.reshape(1,2), axis=0)

  if V_filt == V_lopass:
    title = "Low Pass Filtering"
    figfile = "low_pass_out"
    minorFormatter = ScalarFormatter
    Cnone = Cmin; Lnone = Lmin
  elif V_filt == V_bandpass:
    title = "Band Pass Filtering"
    figfile = "bandpass_out"
    minorFormatter = ScalarFormatter
    Cnone = Cmin; Lnone = Lmax
  elif V_filt == V_hipass:
    title = "High Pass Filtering"
    figfile = "highpassout"
    minorFormatter = ScalarFormatter
    Cnone = Cmax; Lnone = Lmax
  else:
    print("Filter",V_filt,"not recognized")
    return False
  
  Cstr = "%3.0fnF" % (C/1e-12) # in nF
  Lstr = "%4.2f$\mu$H" % (L/1e-6)  # in uH
  plot_output(ax, V, R_S, Cnone, Lnone, R_L, f, "blue",  "none",
              V_filt, Z_filt)
  plot_output(ax, V, R_S, Cnone, L,     R_L, f, "red",   Lstr,
              V_filt, Z_filt)
  plot_output(ax, V, R_S, C,     Lnone, R_L, f, "green", Cstr,
              V_filt, Z_filt)
  plot_output(ax, V, R_S, C,     L,     R_L, f, "brown", "both",
              V_filt, Z_filt)

  ax[0,0].grid(True, which="both")
  ax[0,0].legend()
  ax[0,0].set_title("Amplitude")
  ax[0,0].set_xlabel("Frequency (MHz)")
  ax[0,0].set_ylabel("Output Voltage (V)")

  ax[0,1].grid(True, which="both")
  ax[0,1].set_title("Phase")
  ax[0,1].set_xlabel("Frequency (MHz)")

  ax[1,0].grid(True, which="both")
  ax[1,0].legend()
  ax[1,0].set_title("Amplitude")
  ax[1,0].set_xlabel("Frequency (MHz)")
  ax[1,0].set_ylabel("Input Impedance ($\Omega$)")

  ax[1,1].grid(True, which="both")
  ax[1,1].set_title("Phase")
  ax[1,1].set_xlabel("Frequency (MHz)")
  
  for row in [0,1]:
    for col in [0,1]:
      for axis in [ax[row,col].xaxis, ax[row,col].yaxis]:
        axis.set_major_formatter(ScalarFormatter())
        axis.set_minor_formatter(minorFormatter())
        
  fig1.suptitle(title)
  fig2.suptitle(title)
  fig1.savefig(figfile+"-V.png")
  fig2.savefig(figfile+"-Z.png")
  fig1.show()
  fig2.show()
  return True

def plot_output(ax, V, R_S, C, L, R_L, f, color, label, V_filt, Z_filt):
  """
  """
  expons = expon(V_filt(V, R_S, C, L, R_L, f))
  ax[0,0].loglog(  f/1e6, expons[0], "-", color=color, label=label)
  ax[0,1].semilogx(f/1e6, expons[1]*180/pi, "--", color=color)
  
  Zexpon = expon(Z_filt(C, L, R_L, f))
  ax[1,0].loglog(  f/1e6, Zexpon[0], "-", color=color, label=label)
  ax[1,1].semilogx(f/1e6, Zexpon[1]*180/pi, "--", color=color)

def expon(cmplx_vals):
  """
  convert array of imaginary numbers into exponential format
  
  Equivalent to::
  
    real_part = real(cmplx_vals)
    imag_part = imag(cmplx_vals)
    ampl      = sqrt(real_part**2 + imag_part**2)
    phas      = arctan2(imag_part, real_part)
    return ampl, phas
  
  """
  return abs(cmplx_vals), angle(cmplx_vals)

