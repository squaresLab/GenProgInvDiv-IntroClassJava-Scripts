from multiprocessing import Pool
from subprocess import call
import os
import sys

gp4j_home = os.environ["GP4J_HOME"]


def run(bug):
    (proj, stdnt, rev, mode) = bug #all should be strings
    outfile_name = proj + "_" + stdnt + "_" + rev + "_" + "mode" + mode + ".out"
    outfile = open(outfile_name, "w+")
    print("Starting thread with output: " + outfile_name)
    call(["bash", "runWrapper.sh", proj, stdnt, rev, mode], stdout=outfile, stderr=outfile)
    #arefile_name = proj + "_" + stdnt + "_" + rev + "_" + "mode" + mode + ".are"
    #arefile = open(arefile_name, "w+")
    #seeds
    #bug_dir = "/Users/zhendeveloper/Desktop/LabBox/ProgRepScripts/ICSTest/" + "mode" + mode + "/" + proj + "/" + stdnt + "/" + rev + "/"
    #for seed in range(0, 20):
    #    call(["java", "-cp", gp4j_home+"/target/classes:"+gp4j_home+"/lib/commons-lang3-3.8.1.jar",
    #          "ylyu1.wean.DataProcessor", bug_dir, str(seed)], stdout=arefile, stderr=arefile)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: " + "python3 multi_driver.py PATH_TO_LIST_OF_BUGS_TO_RUN")

    num_threads = 16

    task_list = list()

    bugslist_path = sys.argv[1]
    with open(bugslist_path) as bugslist_file:
        for bugprofile_str in bugslist_file:
            bug = [f.strip() for f in bugprofile_str.split(",")]
            assert len(bug) == 4
            task_list.append(bug)

    p = Pool(num_threads)
    p.map(run, task_list)
