Electronics
===========

provides low level control and monitor capability for electronic instruments.

This package is for basic electronic circuits, and general-purpose instruments 
and interfaces.  The repository is at <https://github.com/SDRAST/Electronics>.

Python 2 versions of code for instruments and interfaces which are specific to 
DSN Radio Astronomy are found in the MonitorControl]
<https://github.jpl.nasa.gov/pages/RadioAstronomy/MonitorControl> repository.

Categories
----------

Circuits
........

Basic filters, impedance matching, plotting frequency responses.

Instruments
...........

Specific devices like power meters
and signal generators.  They are grouped by manufacturers in
sub-subdirectories, each of which is a repository.  For now:
* Instruments_Agilent
* Instruments_Valon

Interfaces
..........

This sub-directory holds the modules for different kinds of interfaces
such as GPIB and USB.  For now:

 * Interfaces_GPIB
 * Interfaces_IOtech
 * Interfaces_LabJack
 * Interfaces_USB

