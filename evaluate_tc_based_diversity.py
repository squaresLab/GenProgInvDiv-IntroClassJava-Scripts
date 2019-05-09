#python 3.5+
import sys
import os
import shutil
import glob
from subprocess import run
from subprocess import PIPE

SEED = 0

class Patch(object):

    def __init__(self, seed, varnum, bugwd):
        self.seed = seed
        self.varnum = varnum
        self.bugwd = bugwd
        self.origpath = self.resolve_origpath(self.bugwd, self.seed)
        self.tsdir = self.make_tsdir(self.bugwd, self.seed, self.origpath)
        self.srcdir = self.resolve_srcdir(self.tsdir)
        self.srcclassname = self.resolve_srcclassname(self.bugwd, self.srcdir)
        self.bytecodedir = self.resolve_bytecodedir(self.tsdir)
        self.evosuite_tsdir = None #placeholder value for ungenerated test suite
        self.evosuite_test_classname = self.resolve_evosuite_test_classname(self.srcclassname)
        self.reports = dict() #maps patches (test suites) to

    def resolve_origpath(self, bugwd, seed):
        return "{}/__testdirSeed{}".format(bugwd, seed) #re-use the patched program from correctness testing

    def make_tsdir(self, bugwd, seed, origpath):
        tsdir = "{}/__evosuiteSeed{}".format(bugwd, seed)
        if not os.path.isdir(tsdir):
            #if tsdir doesn't yet exist, make it and copy stuff to it
            shutil.copytree(origpath, tsdir)
        return tsdir

    def resolve_srcdir(self, tsdir):
        return "{}/src/main/java/".format(tsdir)

    def resolve_srcclassname(self, bugwd, srcdir):
        os.chdir("{}/introclassJava/".format(srcdir))
        srcfile = glob.glob("*.java")[0]
        shortclassname = srcfile.split(".")[0]
        os.chdir(bugwd)
        return "introclassJava.{}".format(shortclassname)

    def resolve_bytecodedir(self, tsdir):
        return "{}/target/classes/".format(tsdir)

    def resolve_evosuite_test_classname(self, srcclassname):
        return "{}_ESTest".format(srcclassname)

    def gen_tests(self):
        self.evosuite_tsdir = "{}/evosuite-tests".format(self.tsdir)
        if os.path.exists(self.evosuite_tsdir):
            print("EvoSuite tests already exist. Not regenerating tests")
        else:
            #hardcoded
            os.chdir(self.tsdir)
            run(["java", "-jar", "/home/user/IntroClassScripts/libs/evosuite-1.0.6.jar", "-class", self.srcclassname,
                 "-projectCP", self.bytecodedir,
                 "-seed", str(SEED), "-Dsearch_budget=60", "-Dstopping_condition=MaxTime", "-criterion", "line"])
            os.chdir(self.bugwd)

    def compile_evosuite_tests_classpath(self):
        #use the patch's own source code for compiling tests
        return self.evosuite_tsdir + \
                ":" + self.bytecodedir + \
                ":{}/lib/junit-4.12.jar".format(os.environ["GP4J_HOME"]) + \
                ":{}/lib/hamcrest-core-1.3.jar".format(os.environ["GP4J_HOME"]) + \
                ":/home/user/IntroClassScripts/libs/evosuite-1.0.6.jar" #hardcode

    def compile_evosuite_tests(self):
        run(["javac", "-classpath", self.compile_evosuite_tests_classpath(), "{}/{}.java".format(self.evosuite_tsdir, self.evosuite_test_classname.replace(".", "/"))])


def run_patch_on_ts(patchsrc, tssrc):
    #todo: implement
    classpath = tssrc.evosuite_tsdir + \
                ":" + patchsrc.bytecodedir + \
                ":{}/lib/junit-4.12.jar".format(os.environ["GP4J_HOME"]) + \
                ":{}/lib/hamcrest-core-1.3.jar".format(os.environ["GP4J_HOME"]) + \
                ":/home/user/IntroClassScripts/libs/evosuite-1.0.6.jar"

    junit_out = run(["java", "-cp", classpath, "org.junit.runner.JUnitCore", tssrc.evosuite_test_classname],
                    stdout=PIPE, stderr=PIPE) #this is a subprocess.CompletedProcess

    print(junit_out.stdout)



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: 1st arg: the bug working directory")
        exit(1)

    bugwd = sys.argv[1]
    bugwd = os.path.abspath(bugwd) #convert to absolute path

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

    #compile after generation
    for p in patches:
        p.compile_evosuite_tests()

    for p in patches:
        for q in patches:
            if p == q: continue
            print("Evaluating seed {}'s patch on seed {}'s generated tests:".format(p.seed, q.seed))
            run_patch_on_ts(p, q)