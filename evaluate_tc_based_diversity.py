#python 3.5+
import sys
import os
import shutil
from subprocess import run

SEED = 0

class Patch(object):

    def __init__(self, seed, varnum, bugwd):
        self.seed = seed
        self.varnum = varnum
        self.bugwd = bugwd
        self.origpath = self.resolve_origpath(self.bugwd, self.seed)
        self.tsdir = self.make_tsdir(self.seed, self.origpath)
        self.targetdir = self.resolve_targetdir(self.tsdir)

    def resolve_origpath(self, bugwd, seed):
        return "{}/__testdirSeed{}".format(bugwd, seed) #re-use the patched program from correctness testing

    def make_tsdir(self, seed, origpath):
        tsdir = "__evosuiteSeed{}".format(seed)
        shutil.copytree(origpath, tsdir)
        return tsdir

    def resolve_targetdir(self, tsdir):
        return "{}/src/main/java/".format(tsdir)

    def gen_tests(self):
        os.chdir(self.tsdir)
        #hardcoded
        run(["java", "-jar", "/home/user/IntroClassScripts/libs/evosuite-1.0.6.jar", "-target", self.targetdir,
             "-seed", SEED, "-Dsearch_budget=60", "-Dstopping_condition=MaxTime"])
        os.chdir(self.bugwd)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: 1st arg: the bug working directory")
        exit(1)

    bugwd = sys.argv[1]

    os.chdir(bugwd)

    #get patches
    patches = list()
    seenseeds = set()
    patcheslistpath = "_patches.csv"
    with open(patcheslistpath) as patcheslist:
        for patchstr in patcheslist:
            parts = patchstr.split(",")
            assert len(parts) == 2
            seed, varnum = parts[0].strip(), parts[1].strip()
            if seed in seenseeds:
                continue
            p = Patch(seed, varnum, bugwd)
            patches.append(p)

    #todo: run evosuite, get test suite reports
    for p in patches:
        print("Now analyzing seed {} variant{}".format(p.seed, p.varnum))
        p.gen_tests()
