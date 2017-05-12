#!/usr/bin/env python

import argparse
import os
import re

# This file is released under terms of BSD license`
# See LICENSE.txt for more information

"""
generate_dep.py

Generate list of all dependencies for a starting fortran file. 
"""

# information
__author__ = 'Valentin Clement'
__copyright__ = 'Copyright 2015, C2SM/MeteoSwiss'
__license__ = 'GPL'
__version__ = '0.1'
__date__ = 'Fri May 12 15:54:44 2017'
__email__ = 'valentin.clement@env.ethz.ch'


def gather_dependencies(fortran_input):
    # open and parse file
    input_file = open(os.path.join(fortran_input), 'r')
    modules = []
    try:
        for line in input_file:
            if use_p.match(line):
                modules.append(mod_p.match(line).group(3))
        return modules
    finally:
        input_file.close()


def get_module_name(fortran_input):
    input_file = open(os.path.join(fortran_input), 'r')
    for line in input_file:
        if mod_p.match(line):


def find_module_file(module_name, src_directory):


    for file in os.listdir(src_directory):
        if file.endswith(".f90"):



parser = argparse.ArgumentParser(description='FORTRAN dependencies scanner.')
parser.add_argument('source', action='store', help='Directory containing the FORTRAN source files')
parser.add_argument('start', action='store', help='Start file for the scanning')
# parser.add_argument('', action='store', help='Output file')
args = parser.parse_args()

use_regex = '^ *(USE|use) +(, *INTRINSIC *::|, *intrinsic *::)? *([^,|^ |^!]*)'
use_p = re.compile(use_regex)

mod_regex = '^ *MODULE *$module_name'
mod_p = re.compile(use_regex)

start_file = args.source + args.start

modules = gather_dependencies(start_file)

for mod in modules:
    print(mod)