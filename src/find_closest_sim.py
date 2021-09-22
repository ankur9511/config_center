#!/usr/bin/env python3
import numpy as np
import sys
import os
import glob
from numpy import linalg as npnorm

def getstrornone(a,varbs):
	value = [s[len(a):] for s in varbs if a in s]
	if not value:
		value = ["none"]
	return value

def parser():
#############
### Variables: Contains the input arguments
### CVfile: Path to the CV file
### col: Column number of order parameter value of interest
### depcol: Additional dependencies in the CV file, such as walls
### center: Location in order parameter space to obtain a seed configuration for
###
	variables = sys.argv[:]
	if len(variables) == 1:
		print ("\n\n###### Options for usage ######\n")
		print ("###### '<>' contain example syntax for use and 'or' is used to differentiate kinds of examples ######\n")
		print ("Mandatory:\n \n\tCVfile=</path/to/CV>  \n\tCVcol=<4A5>  \n\tcenter=<3.4A5.2>  \n\tncols=<10> \n")
		print ("Optional:\n \n\tdepcol=<6>  \n\tprod=<0.6>  \n\toutdir=</path/outputdir/>  \n\tdtCV=<1000>  \n\tgenconf=<y or n> \n")
		print ("If genconf=y :\n \n\tplatform=<gromacs or lammps>\n")
		print ("If platform=gromacs :\n \n\txtcname=</path/xtc-file>  \n\ttprname=</path/tpr-file>  \n\texe=<name-of-executable> \n")
		print ("If platform=lammps :\n \n\twdir=</path/directory/>  \n\texe=<name-of-executable> \n")
		exit()
	
	global CVfile, col, depcol, center, flagdep 
	global ncol, prod, outdir, dt 
	global flaggenconf, MDplatform, exe, xtcname, tprname, wdir
	flaggenconf = 0
	a="CVfile="
	CVfile = getstrornone(a,variables)
	CVfile = str(CVfile[0])

	a="CVcol="
	col = getstrornone(a,variables) 
	try:
		col = np.array(col[0].split('A')).astype(int)
	except ValueError:
		col = 0
		print ("CV column not provided")

	a="depcol="
	depcol = getstrornone(a,variables)
	depcol = depcol[0].split('A')
	flagdep = 0
	for dep in depcol:
		if dep == 'none':
			flagdep = -1
			break

	a="center="
	center = getstrornone(a,variables)
	try:
		center = np.array(center[0].split('A')).astype(float)
	except ValueError:
		center = "none"
		print ("You have not provided center of interest")

	a="ncols="
	ncol = getstrornone(a,variables)
	ncol = int(ncol[0])

	a="prod="
	prod = getstrornone(a,variables)
	try:
		prod = float(prod[0])
	except ValueError:
		prod = 0.75

	a="outdir="
	outdir = getstrornone(a,variables) 
	outdir = str(outdir[0])
	if outdir == "none":
		outdir = "${PWD}/"

	a="dtCV="
	dt = getstrornone(a,variables) 
	try:
		dt = int(dt[0])
	except ValueError:
		dt = 1000
		print ("Timesteps between consequetive CV datapoint not provided") 

	a="genconf="
	genconf = getstrornone(a,variables) 
	genconf = str(genconf[0])
	if "y" == genconf[0] or "Y" == genconf[0]:
		flaggenconf = 1
		a="platform="
		MDplatform = getstrornone(a,variables) 
		MDplatform = str(MDplatform[0])
		if MDplatform == "gromacs":
			a="xtcname="
			xtcname = getstrornone(a,variables) 
			xtcname = str(xtcname[0])
			if xtcname == "none":
				xtcname = "gmxexample.xtc"
			a="tprname="
			tprname = getstrornone(a,variables) 
			tprname = str(tprname[0])
			if tprname == "none":
				tprname = "gmxexample.tpr"
		if MDplatform == "lammps":
			a="wdir="
			wdir = getstrornone(a,variables) 
			wdir = str(wdir[0])
			if wdir == "none":
				wdir = "/project/palmer/Ankur/code_find_next_simulation/"
		a="exe="
		exe = getstrornone(a,variables) 
		exe = str(exe[0])

def CVfiletodata():
	global CVfile, col, depcol, center, flagdep, ncol
	global data
	data = np.empty((0,ncol))
	if flagdep == -1:
		with open(glob.glob(CVfile)[0],'r') as f:
			tdata=f.read().split('\n')
			lenfread = len(tdata)
			fread = iter(tdata)
			j = 0
			flag = 1
			n = 0
			while j < lenfread:
				i = next(fread)
				j = j+1
				if ("FIELDS" in i):
					flag = -1
					continue
				if (flag < 0):
					flag = flag+1
					continue
				flag = 1
				t = np.array(i.split(),order='F').astype(float)
				t = t.reshape((1,len(t)))
				if (t.shape[1]==data.shape[1]):
					data = np.append(data,t,axis=0)
					n = n+1
	else:
		with open(glob.glob(CVfile)[0],'r') as f:
			tdata=f.read().split('\n')
			lenfread = len(tdata)
			fread = iter(tdata)
			j = 0
			flag = 1
			n = 0
			while j < lenfread:
				i = next(fread)
				j = j+1
				if ("FIELDS" in i):
					flag = -1
					continue
				if (flag < 0):
					flag = flag+1
					continue
				flag = 1
				t = np.array(i.split(),order='F').astype(float)
				t = t.reshape((1,len(t)))
				if (t.shape[1]==data.shape[1]):
					if np.all((t[np.array(depcol).astype(int)[:]] == 0)):
						data = np.append(data,t,axis=0)
						n = n+1
def CVdist(centerCV,dataCV,colCV):
	return npnorm.norm(dataCV[:,colCV[:]] - centerCV[:], axis=1)

parser()
CVfiletodata()
datachop = data[int(prod*data.shape[0]):,:]
confindex = np.argmin(CVdist(center, datachop, col))
time = datachop[confindex,0]
timestep = time*dt
time = int(time)
print("Closest configuration is at: ",time," ps, ~",timestep,
      " timestep, ", "at O.P. value = ",datachop[confindex,col[:]])

if flaggenconf == 1:
	if MDplatform == "gromacs":
		command = "echo 0 | "+ exe +" trjconv -f "+ \
                          xtcname+" -s "+tprname+" -b "+ \
                          str(time)+" -e "+str(time)+ \
                          " -o "+outdir+"/conf.gro"
	elif MDplatform == "lammps":
		timestep = int(timestep/1000)*1000
		command = exe+" -var wdir "+ wdir + \
                          " -var outdir "+outdir + \
                          " -var timeconfig "+ str(timestep) + \
                          " -in lmptrj2res"
	print (command)
	os.system(command)
