#!/bin/bash
default:
	# Default options
	#
	# make test_gromacs : creates test tool for use with gromacs
	# make test_lammps : creates test tool for use with lammps
	#
	# Tool name after make
	#
	# testsimtool
	#

test_gromacs:
	@echo "alias testsimtool=${PWD}/src/find_closest_sim.py" > loadenv
	@cp tests_commit/gmxexample .
	@chmod +x gmxexample
	# The test can be performed
	# by loading environment: 
	@echo 'source loadenv'
	# and running lmpexample: 
	@echo 'source gmxexample'

test_lammps:
	@echo "alias testsimtool=${PWD}/src/find_closest_sim.py" > loadenv
	@cp tests_commit/lmpexample .
	@cp tests_commit/lmptrj* .
	@chmod +x lmpexample
	# The test can be performed
	# by loading environment: 
	@echo 'source loadenv'
	# and running lmpexample: 
	@echo 'source lmpexample'

clean:
	@rm -f *conf*
	@rm -f gmx*
	@rm -f loadenv
	@rm -f lmp*
	@rm -f log*
	# Files deleted
