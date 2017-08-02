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
                modules.append(use_p.match(line).group(2).lower().decode('string_escape'))
        return list(set(modules))
    finally:
        input_file.close()


# Try to find the file containing the specified module
def find_module_file(module_name, module_map):
    if module_name in module_map:
        return module_map[module_name.lower()]
    return None


# Recursive call to process all dependencies
def find_all_dependencies(mods, module_map, src_directory, excluded):
    for mod in mods:
        mod_file = find_module_file(mod, module_map)
        if mod_file is not None and mod_file.replace(src_directory, '') not in excluded:
            if mod not in processed_modules:
                usages = gather_dependencies(mod_file)
                if mod in usages:
                    print('Warning: Module ' + mod + ' use itself!', file=sys.stderr)
                    usages.remove(mod)
                if len(usages) > 0:
                    find_all_dependencies(usages, module_map, src_directory, excluded)
                processed_modules.append(mod)
                print(mod_file.replace(src_directory, ''))
        else:
            if mod in intrinsic_modules:
                intrinsic_usage[mod] = intrinsic_usage[mod] + 1
            else:
                print('Warning: no file found for module ' + mod.rstrip(), file=sys.stderr)


# Gather all fortran files in the source directory. For the moment only .f90 files
def find_all_fortran_files(is_recursive, src_directory):
    fortran_files = []
    if is_recursive:
        for root, dirs, files in os.walk(src_directory):
            for input_file in files:
                if input_file.endswith('.f90'):
                    fortran_files.append(root + '/' + input_file)
    else:
        for input_file in os.listdir(src_directory):
            if input_file.endswith(".f90"):
                fortran_files.append(os.path.join(src_directory, input_file))
    return fortran_files


# Map module name with their corresponding files
def find_all_modules(fortran_files):
    mapping = dict()
    mod_generic_regex = '^ *MODULE * ([a-zA-Z0-9_]+)'
    mod_generic_p = re.compile(mod_generic_regex, re.IGNORECASE)
    for f90 in fortran_files:
        fortran_file = open(f90, 'r')
        for line in fortran_file:
            if mod_generic_p.match(line):
                module_name = mod_generic_p.match(line).group(1)
                if module_name.lower() != 'procedure':
                    mapping[module_name] = f90
    return mapping


# Arguments of the program
parser = argparse.ArgumentParser(description='FORTRAN dependency scanner.')
parser.add_argument('source', action='store', help='Directory containing the FORTRAN source files')
parser.add_argument('start', action='store', help='Start file for the scanning')
parser.add_argument('--recursive', dest='recursive', action='store_true', help='Recurse to child folders')
parser.add_argument('--exclude', dest='exclude_list', action='store',
                    help='List of file to be excluded seperated by a colon :')
parser.set_defaults(recursive=False)
parser.set_defaults(exclude_list='')
args = parser.parse_args()

# List of FORTRAN intrinsic modules
intrinsic_modules = ['iso_c_binding', 'iso_fortran_env', 'openacc', 'omp_lib', 'omp_lib_kinds']
fortran_ext = ['f90', 'F90', '.for', '.f', '.F', '.f95', '.f03']
intrinsic_usage = dict()
for intrinsic_module in intrinsic_modules:
    intrinsic_usage[intrinsic_module] = 0

# all excluded files
excluded_files = args.exclude_list.split(':')

# Regex to catch the module names in use statements
use_regex = '^ *USE *(, *INTRINSIC *::)? *([^,|^ |^!]*)'
use_p = re.compile(use_regex)

# Format the entry point
start_file = os.path.join(args.source, args.start)

# Find all the FORTRAN file in the search path
input_files = find_all_fortran_files(args.recursive, args.source)

# Process all module files once to extract their module
module_to_file = find_all_modules(input_files)

# Keep list of processed modules to avoid processing them more than once
processed_modules = []

# Start the dependency search from the given entry point (file containing the PROGRAM subroutine)
start_modules = gather_dependencies(start_file)
find_all_dependencies(start_modules, module_to_file, args.source, excluded_files)

# Print the entry point as the last file in the dependency list
print(start_file.replace(args.source, ''))

# Check files that have not been processed
processed_module_files = [start_file.replace(args.source, '')]
for processed_module in processed_modules:
    module_file = find_module_file(processed_module, module_to_file)
    processed_module_files.append(module_file)

# Check module that have not been processed to have all .xmod
for k in module_to_file:
    module_file = module_to_file[k].replace(args.source, '')
    if k not in processed_modules and module_file not in excluded_files:
        start_modules = gather_dependencies(module_to_file[k])
        find_all_dependencies(start_modules, module_to_file, args.source, excluded_files)
        processed_modules.append(k)
        for key in module_to_file:
            if module_file in module_to_file[key]:
                processed_modules.append(key)

# Process rest of files that are not excluded
for input_file in input_files:
    if input_file not in processed_module_files and input_file.replace(args.source, '') not in excluded_files:
        print (input_file.replace(args.source, ''))

# Print intrinsic module usage
for intrinsic_module in intrinsic_modules:
    if intrinsic_usage[intrinsic_module] > 0:
        print('Info: intrinsic module ' + intrinsic_module + ' used ' + str(intrinsic_usage[intrinsic_module])
              + ' times', file=sys.stderr)
