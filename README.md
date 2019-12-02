# fdependencies
List dependencies of Fortran program

[![Build Status](https://travis-ci.org/claw-project/fdependencies.svg?branch=master)](https://travis-ci.org/claw-project/fdependencies)

```
usage: generate_dep.py [-h] [--recursive] [--exclude EXCLUDE_LIST] source start

Fortran dependency scanner.

positional arguments:
  source                 Directory containing the Fortran source files
  start                  Start file for the scanning

optional arguments:
  -h, --help                show this help message and exit
  --recursive               Recurse to child folders
  --exclude EXCLUDE_LIST    List of file to be excluded separated by a colon :
  --exclude-dir EXCLUDE_DIR Directory to be excluded
  --stop-after-start        Stop after reaching dependency for the start file
```
