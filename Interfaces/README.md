## Support for Instrument Interfaces

Support for instrument communication protocols.

USB, GPIB, etc. are obvious protocols.  After some thought, I decided that LabJacks and IOtech cards and chassis have a higher level of protocol but are general enough to be included here.  Also, the APC power distribution unit support, which uses the SNMP protocol, is here. Conceivably we might add SICL
and VXI later.

Each bus has its own sub-directory and repository.  For now:
* GPIB      \(repository Electronics_Interfaces_GPIB\)
* IOtech    \(repository Electronics_Interfaces_IOtech\)
* LabJack   \(repository Electronics_Interfaces_LabJack\)
* SNMP      \(repository Electronics_Interfaces_SNMP\)
* USB       \(repository Electronics_Interfaces_USB\)

### Warning

Sub-directory Electronics.Interfaces is part of the Electronics project.
'git commit' inside this directory does not commit any changes in its
sub-directories.