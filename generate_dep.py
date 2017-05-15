#!/usr/bin/env python

from __future__ import print_function
import argparse
import os
import re
import sys

# This file is released under terms of BSD license`
# See LICENSE.txt for more information

"""
generate_dep.py

Generate list of all dependencies for a starting fortran file. 
"""

# information
__author__ = 'Valentin Clement'
__copyright__ = 'Copyright 2017, C2SM/MeteoSwiss'
__license__ = 'GPL'
__version__ = '0.1'
__date__ = 'Fri May 12 15:54:44 2017'
__email__ = 'valentin.clement@env.ethz.ch'


# Gather all use information from the file
def gather_dependencies(fortran_input):
    input_file = open(os.path.join(fortran_input), 'r')
    modules = []
    try:
        for line in input_file:
            if use_p.match(line):
                modules.append(use_p.match(line).group(3))
        return modules
    finally:
        input_file.close()


# Try to find the file containing the specified module
def find_module_file(module_name, src_directory):
    mod_regex = '^ *MODULE *' + module_name
    mod_p = re.compile(mod_regex)
    for input_file in os.listdir(src_directory):
        if input_file.endswith(".f90"):
            fortran_file = open(os.path.join(src_directory, input_file), 'r')
            for line in fortran_file:
                if mod_p.match(line):
                    return os.path.join(src_directory, input_file)


# Recursive call to process all dependencies
def find_all_dependencies(mods):
    for mod in mods:
        mod_file = find_module_file(mod, args.source)
        if mod_file is not None:
            if mod not in processed_modules:
                usages = gather_dependencies(mod_file)
                if len(usages) > 0:
                    find_all_dependencies(usages)
                processed_modules.append(mod)
                print(os.path.basename(mod_file))
        else:
            print('Warning: no file found for module ' + mod, file=sys.stderr)


parser = argparse.ArgumentParser(description='FORTRAN dependencies scanner.')
parser.add_argument('source', action='store', help='Directory containing the FORTRAN source files')
parser.add_argument('start', action='store', help='Start file for the scanning')
args = parser.parse_args()

use_regex = '^ *(USE|use) +(, *INTRINSIC *::|, *intrinsic *::)? *([^,|^ |^!]*)'
use_p = re.compile(use_regex)

start_file = os.path.join(args.source, args.start)

processed_modules = []
start_modules = gather_dependencies(start_file)
find_all_dependencies(start_modules)

print(os.path.basename(start_file))
