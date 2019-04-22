This README is outdated, don't use until further notice (steps 1,2,3 are still good though).

Instructions for running genprog4java w/ invariant diversity for IntroClassJava:

1. Get IntroClassJava by cloning this repo: https://github.com/Spirals-Team/IntroClassJava

2. Run `preprocessIntroClassJava.sh` with the following argument:
    1. Path to IntroClassJava
    
    e.g: `bash preprocessIntroClassJava.sh ~/wherever/IntroClassJava/`
    
    This script will shorten the student names to the first 4 chars.

3. Set the following global variables:
    1. `GP4J_HOME=path to genprog4java`
    2. `DAIKONDIR=path to daikon`
    3. `ICJ_HOME=path to IntroClassJava`
    4. `ICJ_OUT_DIR=path to the directory to store copies of IntroClassJava bugs. GenProg4Java will operate on these bugs.`
    5. `JAVA_HOME=path to java8 installation`

4. Edit the following variables in runWrapper.sh
    1. `SSED=starting seed`
    2. `ESED=ending seed`

5. If you wish to run a single bug, call runWrapper.sh with the following arguments:
    1. Project (checksum, median, ...)
    2. Student identifier (08c7, 2c15, ...)
    3. Revision number (000, 006, ...)
    4. Repair mode (0 for original GenProg, 4 for invariant diversity)
    
    e.g: `bash runWrapper.sh checksum 08c7 006 4`

6. If you wish to concurrently run multiple bugs, first create a file with a list of 
the bugs that you wish to run. On each line of the file, indicate the bug that you 
wish to run as follows: `project,studentid,revision,repairmode`

    For example, to run `checksum/08c7/006/` on original Genprog (mode 0) and 
    `median/ocdf/003` on invariant diversity search (mode 4), create a file 
    with the following content:
    
    ```
    checksum,08c7,006,0
    median,ocdf,003,4
    ```

    Then, run `multi_driver.py` using Python 3 with the following argument:
    1. Path to the file containing the aforementioned list of bugs to run.
    
    e.g: `python3 multi_driver.py wherever/list_of_bugs_to_run`
    
