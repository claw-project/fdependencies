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
                modules.append(use_p.match(line).group(3).lower())
        return modules
    finally:
        input_file.close()


# Try to find the file containing the specified module
def find_module_file(module_name, module_map):
    if module_name in module_map:
        return module_map[module_name.lower()]
    return None


# Recursive call to process all dependencies
def find_all_dependencies(mods, module_map, src_directory):
    for mod in mods:
        mod_file = find_module_file(mod, module_map)
        if mod_file is not None:
            if mod not in processed_modules:
                usages = gather_dependencies(mod_file)
                if len(usages) > 0:
                    find_all_dependencies(usages, module_map, src_directory)
                processed_modules.append(mod)
                print(mod_file.replace(src_directory, ''))
        else:
            print('Warning: no file found for module ' + mod, file=sys.stderr)


# Gather all fortran files in the source directory. For the moment only .f90 files
def find_all_fortran_files(is_recusrive, src_directory):
    fortran_files = []
    if is_recusrive:
        for root, dirs, files in os.walk(src_directory):
            for input_file in files:
                if input_file.endswith('.f90'):
                    fortran_files.append(root + '/' + input_file)
    else:
        for input_file in os.listdir(src_directory):
            if input_file.endswith(".f90"):
                fortran_files.append(input_file)
    return fortran_files


# Map module name with their corresponding files
def find_all_modules(fortran_files):
    mapping = dict()
    mod_generic_regex = '^ *MODULE * ([a-zA-Z1-9_]+)'
    mod_generic_p = re.compile(mod_generic_regex)
    for f90 in fortran_files:
        fortran_file = open(f90, 'r')
        for line in fortran_file:
            if mod_generic_p.match(line):
                module_name = mod_generic_p.match(line).group(1)
                mapping[module_name] = f90
    return mapping


parser = argparse.ArgumentParser(description='FORTRAN dependencies scanner.')
parser.add_argument('source', action='store', help='Directory containing the FORTRAN source files')
parser.add_argument('start', action='store', help='Start file for the scanning')
parser.add_argument('--recursive', dest='recursive', action='store_true')
parser.set_defaults(recursive=False)
args = parser.parse_args()

use_regex = '^ *(USE|use) +(, *INTRINSIC *::|, *intrinsic *::)? *([^,|^ |^!]*)'
use_p = re.compile(use_regex)

start_file = os.path.join(args.source, args.start)
input_files = find_all_fortran_files(args.recursive, args.source)
module_to_file = find_all_modules(input_files)

processed_modules = []
start_modules = gather_dependencies(start_file)
find_all_dependencies(start_modules, module_to_file, args.source)

print(start_file.replace(args.source, ''))
