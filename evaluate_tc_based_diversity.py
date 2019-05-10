
#python 3.5+
import sys
import os
import shutil
import glob
import re
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
        self.failed_tests = dict() #maps patches (test suites) to failed tests
        self.semantic_distance_not_normalized = dict() #maps patches p to the semantic distance between self and p
        self.semantic_diversity_not_normalized = 0
        self.num_of_evosuite_tests = 0

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

    def get_normalized_semantic_diversity_score(self):
        total_num_tests = sum([p.num_of_evosuite_tests for p in self.failed_tests.keys()])
        return self.semantic_diversity_not_normalized / total_num_tests

#input: the output (string form) of a junit test execution
#output: (a set of failing test cases (method names of tests as strings), the number of tests ran)
def process_junit_output(output):
    failed_tests = set()
    num_tests = None

    failure_description_started = False

    for line in output.splitlines():
        line = line.strip()
        if re.search("\AThere (was|were) [0-9]+ failures?:", line):
            failure_description_started = True
            continue
        if failure_description_started:
            failed_test_pattern = "\A[0-9]+\) (test[0-9]+)\("
            test = re.findall(failed_test_pattern, line)
            assert len(test) <= 1 #num of tests should only be zero or one per line
            for t in test:
                failed_tests.add(t)

            num_tests_regex_found = re.findall("\ATests? run: ([0-9]+)", line)
            if len(num_tests_regex_found) == 1:
                num_tests = num_tests_regex_found[0]
        else:
            num_tests_regex_found = re.findall("\AOK \(([0-9]+) tests?\)", line)
            if len(num_tests_regex_found) == 1:
                num_tests = num_tests_regex_found[0]

    return (failed_tests, int(num_tests))

def run_patch_on_ts(patchsrc, tssrc):
    classpath = tssrc.evosuite_tsdir + \
                ":" + patchsrc.bytecodedir + \
                ":{}/lib/junit-4.12.jar".format(os.environ["GP4J_HOME"]) + \
                ":{}/lib/hamcrest-core-1.3.jar".format(os.environ["GP4J_HOME"]) + \
                ":/home/user/IntroClassScripts/libs/evosuite-1.0.6.jar"

    junit_out = run(["java", "-cp", classpath, "org.junit.runner.JUnitCore", tssrc.evosuite_test_classname],
                    stdout=PIPE, stderr=PIPE) #this is a subprocess.CompletedProcess

    failures, num_tests = process_junit_output(junit_out.stdout.decode())
    print(failures, num_tests)
    patchsrc.failed_tests[tssrc] = failures
    tssrc.num_of_evosuite_tests = num_tests

def set_sem_dist(patch1, patch2):
    if patch2 in patch1.semantic_distance_not_normalized or patch1 in patch2.semantic_distance_not_normalized:
        return #distances are already calculated
    assert set(patch1.failed_tests.keys()) == set(patch2.failed_tests.keys())  # assume patches used for evosuite were the same
    dist = 0
    for p in patch1.failed_tests.keys():
        p1_failed_tests = patch1.failed_tests[p]
        p2_failed_tests = patch2.failed_tests[p]
        dist_respect_to_p = len(p1_failed_tests.symmetric_difference(p2_failed_tests))
        dist += dist_respect_to_p
    patch1.semantic_distance_not_normalized[patch2] = patch2.semantic_distance_not_normalized[patch1] = dist
    patch1.semantic_diversity_not_normalized += dist
    patch2.semantic_diversity_not_normalized += dist

#todo: normalize semantic distance & diversity by number of test cases

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
            #if seed in seenseeds:
            #    continue
            p = Patch(seed, varnum, bugwd)
            patches.append(p)

    for p in patches:
        print("Now analyzing seed {} variant{}".format(p.seed, p.varnum))
        p.gen_tests()

    #compile after generation
    for p in patches:
        p.compile_evosuite_tests()

    #construct test case profiles by seeing which tests fail
    for p in patches:
        for q in patches:
            print("Evaluating seed {}'s patch on seed {}'s generated tests:".format(p.seed, q.seed))
            run_patch_on_ts(p, q)

    #calculate semantic distance (& diversity)
    for p in patches:
        for q in patches:
            if p == q: continue
            set_sem_dist(p, q)

    for p in patches:
        print("Normalized diversity of seed {} is {}, number of generated tests is {}"
              .format(p.seed, p.get_normalized_semantic_diversity_score(), p.num_of_evosuite_tests))

