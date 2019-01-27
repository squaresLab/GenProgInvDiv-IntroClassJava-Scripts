import sys
import os

def partition(bugs, n):
    if n >= len(bugs): return [[b] for b in bugs]
    size_lo = len(bugs) // n
    size_hi = size_lo + 1
    num_hi = len(bugs) % n
    num_lo = n - num_hi

    partitions = list()
    i = 0
    for whocares in range(num_hi):
        partitions.append(bugs[i:i+size_hi])
        i += size_hi

    for whocares in range(num_lo):
        partitions.append(bugs[i:i+size_lo])
        i += size_lo
    return partitions

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("1st arg: path to file w/ list of bugs (proj, student, rev, mode) to run")
        print("2nd arg: path to file w/ IPs of servers (each IP on a line)")
        print("3rd arg: directory to put files w/ lists of bugs assigned to each ip")
        exit(1)

    bugslist_path = sys.argv[1]
    ips_path = sys.argv[2]
    wkld_assgn_dir_path = sys.argv[3]

    os.makedirs(wkld_assgn_dir_path, exist_ok=True)

    allbugs = open(bugslist_path).read().splitlines(keepends=False)
    allips = open(ips_path).read().splitlines(keepends=False)
    workloads = partition(allbugs, len(allips))

    for i in range(len(allips)):
        wkld = workloads[i]
        ip = allips[i]
        wkld_file_path = wkld_assgn_dir_path + "/bugsList"
        with open(wkld_file_path, "w") as outfile:
            outfile.writelines(wkld)
        login = "zhenyud@" + ip
        os.system("scp " + wkld_file_path + " " + login + ":IntroClassScripts/")
        #rename file locally
        wkld_file_path_local = wkld_file_path + "_" + ip
        os.system("mv " + wkld_file_path + " " + wkld_file_path_local)
        bugslist_on_server = "bugsList"
        #runcmd = "ssh " + login + " \"source .bashrc;cd IntroClassScripts/;(nohup python single_driver.py " + bugslist_on_server + " " \
        #         + "/data" + " &> " + "/data/driver.out &)\""
        runcmd = "ssh " + login + " 'bash run.sh'"
        print(runcmd)
        os.system(runcmd)