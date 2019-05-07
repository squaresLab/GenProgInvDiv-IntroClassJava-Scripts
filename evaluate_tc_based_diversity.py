import sys
import os
import shutil

#get hardcoded path for docker containers

class Patch(object):

    def __init__(self, seed, varnum, bugwd):
        self.seed = seed
        self.varnum = varnum
        self.origpath = self.resolve_origpath(self)
        self.tsdir = self.make_tsdir(self)

    def resolve_origpath(self):
        return "{}/__variantsSeed{}/{}/tmp/variant{}".format(self.bugwd, self.seed, self.bugwd, self.varnum)

    def make_tsdir(self):
        tsdir = "--evosuiteSeed{}".format(self.seed)
        os.mkdir(tsdir)
        shutil.copytree()
        return tsdir

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: 1st arg: the bug working directory")
        exit(1)

    bugwd = sys.argv[1]

    os.chdir(bugwd)

    patches = list() #list of tuples: (seed, varnum)
    patcheslistpath = "_patches.csv"
    with open(patcheslistpath) as patcheslist:
        for patchstr in patcheslist:
            parts = patchstr.split(",")
            assert len(parts) == 2
            patches.append((parts[0].strip(), parts[1].strip()))

    #todo: get patches, run evosuite, get test suite reports
