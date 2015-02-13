# Configuration

In this directory all the required configuration files, etc... are included in YAML sintax.

## Contents

* Hardwares: the list of all the hardware platforms that can be used in the .feature files (see below for details)
* IDEs: the list of all the Arduino IDEs installed locally (see below for details).
* Sketch: extra options about sketches (see below for details)

### Hardwares

Each entry is the name of a hardware platform. Currently the content is:

* port: the serial port in which the platform is attached
* timeout: maximum time to wait for answer on this platform
* Substitutions: a list of the 'tokens' to be replaced in sketchs, outputs and sequences.

### IDEs

Each entry is a description of a Arduino software platform installed locally. Currently the content is:

* Path: where the IDE is installed.
* (optional) CompileVerion: the detailed version of the IDE, currently it is not needed.
    
### Sketchs

Detailed or options about sketches, currently it have only one 'Substitutions' section in which replacaments of token for all the hardware platforms can be included.
