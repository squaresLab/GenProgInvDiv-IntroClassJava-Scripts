#python 3

import os
import glob
import sys
from subprocess import call

def check_patch(wd, seed, variant):
	variantsdir = "variantsSeed{}".format(seed)
	variants_archive = variantsdir + ".tar"
	
	os.chdir(wd)
	os.mkdir(variantsdir)
	call(["tar", "-xf", variants_archive,  "-C", variantsdir])
	os.chdir(variantsdir + "/home/user/output/")
	middledir = glob.glob("*/")[0]
	patchdir = variantsdir + "/home/user/output/" + middledir + "/tmp/" + "variant{}/".format(variant)
	
	os.chdir(wd)
	testdir = "testdir"
	os.mkdir(testdir)
	#todo: copy icj bug from $icj_dir to testdir, then replace the source files, then mvn test :) 

if __name__ = "__main__":
	if len(sys.argv) != 3:
		print("Usage: 1st argument: working directory for the repaired introclass bug to analyze\n" +
			"2nd argument: csv file in the format of: seed with repair, variant number of repair\n")
		exit(1)
	bugwd = sys.argv[1] + "/"
	repairsfile_path = sys.argv[2]
	with open(repairsfile_path) as repairsfile:
		for repairline in repairsfile:
			repairline_parts = repairline.split(',')
			assert len(repairline_parts) == 2
			seednum = repairline_parts[0].strip()
			varnum = repairline_parts[1].strip()
			check_patch(bugwd, seednum, varnum)
