#python 3

import os
import glob
import sys
import shutil
from subprocess import call

#all temp directories made should have a double underscore prefix to denote that the directory contains files associated with checking patch correctness
def check_patch(wd, seed, variant):
	print("\n\nEVALUATING SEED {} variant{}\n\n".format(seed, variant))
	sys.stdout.flush()
	variantsdir = "__variantsSeed{}".format(seed)
	variants_archive = variantsdir[2:] + ".tar"

	os.chdir(wd)
	os.mkdir(variantsdir)
	call(["tar", "-xf", variants_archive,  "-C", variantsdir])
	os.chdir(variantsdir + "/home/user/output/")
	middledir = glob.glob("*/")[0]
	patchdir = "{}/home/user/output/{}/tmp/variant{}/introclassJava/".format(variantsdir, middledir, variant)

	os.chdir(wd)
	testdir = "__testdirSeed{}/".format(seed)
	#os.mkdir(testdir) #testdir must not already exist, otherwise shutil.copytree won't work
	#copy icj bug from $icj_dir to testdir, then replace the source files, then mvn test :) 
	middir_parts = middledir.split("_")
	proj, stdnid, atmptid = middir_parts[0:3]
	icjhome = os.environ["ICJ_HOME"]
	origbugdir = "{}/dataset/{}/{}/{}/".format(icjhome, proj, stdnid, atmptid)
	shutil.copytree(origbugdir, "{}/{}".format(wd, testdir))

	#replace source code in testdir with source code from patchdir
	patchsrc = glob.glob("{}*.java".format(patchdir))[0]
	patchdest = glob.glob("{}src/main/java/introclassJava/*.java".format(testdir))[0]
	shutil.copyfile(patchsrc, patchdest)
	os.chdir(testdir)
	call(["mvn", "test"])
	sys.stdout.flush()

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Usage: 1st argument: working directory for the repaired introclass bug to analyze\n" +
			"2nd argument: csv file in the format of: seed with repair, variant number of repair\n")
		exit(1)
	bugwd = os.path.abspath(sys.argv[1]) + "/"
	repairsfile_path = sys.argv[2]
	with open(repairsfile_path) as repairsfile:
		for repairline in repairsfile:
			repairline_parts = repairline.split(',')
			assert len(repairline_parts) == 2
			seednum = repairline_parts[0].strip()
			varnum = repairline_parts[1].strip()
			check_patch(bugwd, seednum, varnum)
