# M&C for Electronic Instruments

provides low level control and monitor capability for electronic instruments.

This package is for general-purpose instruments and interfaces.  Instruments and interfaces which are specific to DSN Radio Astronomy are found in the [MonitorControl](https://github.jpl.nasa.gov/pages/RadioAstronomy/MonitorControl) repository.

View the [source code documentation](https://github.jpl.nasa.gov/pages/RadioAstronomy/Electronics) for the entire tree.

## Categories

### Instruments

This sub-directory holds the modules for specific devices like power meters
and signal generators.  They are grouped by manufacturers in
sub-subdirectories, each of which is a repository.  For now:
* Instruments_Agilent
* Instruments_Valon

### Interfaces

This sub-directory holds the modules for different kinds of interfaces
such as GPIB and USB.  For now:
* Interfaces_GPIB
* Interfaces_IOtech
* Interfaces_LabJack
* Interfaces_USB

### Warning

Committing changes in this directory does not commit any changes in these
sub-directories.  Get used to doing commits while in them.

## Dependencies

The .dot and .png files were created with snakefood in the site-packages Observatory package before transfer to DSN-Sci-packages.  They show the interdependecies for the Instruments and Interfaces packages at the time of creation.  Do not count on them being up to date.
