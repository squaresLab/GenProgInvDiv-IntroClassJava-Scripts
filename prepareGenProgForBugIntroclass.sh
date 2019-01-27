#!/bin/bash

#The purpose of this script is to set up the environment to run Z&Y's GenProg extension of a particular Introclass bug.

if [ "$#" -ne 3 ]; then
    echo "1st param is the path to the directory containing the Introclass bug"
    echo "2nd param is the java8 installation"
    echo "3th param is the mode number, indicating which search strategy to use (0 for genprog, 4 for diversity)"
else

GP4J_HOME=/home/lvyiwei1/genprog4java-branch/genprog4java

BUGPATH=$1
DIROFJAVA8=$2
INVCHKMODE=$3

BASEDIR=$PWD

#compile & run the test suite for the bug, and collect the surefire-reports
cd ${BUGPATH}
cp ~/bench/mode4/median/median_* src/main/java/introclassJava
echo "Running the bug's test suite, expect to see build failure-this is normal."
mvn test
SUREFIRE="$BUGPATH/target/surefire-reports"

#generate pos.tests and neg.tests
cd ${BASEDIR}
POSTESTS="$BUGPATH/pos.tests"
NEGTESTS="$BUGPATH/neg.tests"
python3 get_pos_neg_tests.py ${SUREFIRE} ${POSTESTS} ${NEGTESTS}

#separate pos & neg test classes
cd "separateTests"
SEPARATETESTSCP=".:javaparser_javaparser-core_target_classes/"
#if [ "SeparateTests.java" -nt "SeparateTests.class" ]; then
#    echo "recompiling SeparateTests.java since it either doesn't exist or is out of date"
    javac -classpath ${SEPARATETESTSCP} "SeparateTests.java"
#fi
SEPARATEDTESTS="$BUGPATH/src/test-processed"
mkdir ${SEPARATEDTESTS}
OLDTESTCLASSES="$BUGPATH/src/test/java"
java -cp ${SEPARATETESTSCP} "SeparateTests" ${POSTESTS} ${NEGTESTS} ${SEPARATEDTESTS} ${OLDTESTCLASSES}

#change timeouts from 1000 to 3000
sed -i.sedtemp 's/(timeout = 1000)/(timeout = 3000)/g' $SEPARATEDTESTS/introclassJava/PositiveTest.java
sed -i.sedtemp 's/(timeout = 1000)/(timeout = 3000)/g' $SEPARATEDTESTS/introclassJava/NegativeTest.java
rm $SEPARATEDTESTS/introclassJava/*.sedtemp

#replace old tests w/ the new separated tests
rm -r ${OLDTESTCLASSES}/introclassJava/
mv $SEPARATEDTESTS/introclassJava/ $OLDTESTCLASSES/
rm -r ${SEPARATEDTESTS}
SEPARATEDTESTS=${OLDTESTCLASSES}

#rebuild w/ new separated tests
cd ${BUGPATH}
mvn test-compile

#make no-timeout positive tests for Daikon
DAIKONTESTS="$BUGPATH/src/test-daikon"
mkdir ${DAIKONTESTS}
mkdir "$DAIKONTESTS/introclassJava"
cp "$SEPARATEDTESTS/introclassJava/PositiveTest.java" "$DAIKONTESTS/introclassJava/" #i know hardcoding is bad, but time is short
DAIKONPOSTEST="$DAIKONTESTS/introclassJava/PositiveTest.java"
sed -i.sedtemp 's/(timeout = [0-9]*)//g' ${DAIKONPOSTEST}
rm ${DAIKONPOSTEST}.sedtemp

echo "compiling positive tests w/o timeouts for Daikon"
cd ${DAIKONTESTS}
TESTCP=".:$BUGPATH/target/classes:$BUGPATH/target/test-classes:$GP4J_HOME/lib/junit-4.12.jar:$GP4J_HOME/lib/hamcrest-core-1.3.jar"
javac -classpath ${TESTCP} ${DAIKONPOSTEST}

#get class names to be repaired
cd "$BUGPATH"
basename $(ls "src/main/java/introclassJava/") .java > bugfilestemp.txt
printf "introclassJava." | cat - bugfilestemp.txt > bugfiles.txt
rm bugfilestemp.txt


#create runCompile.sh

FILE=$BUGPATH/runCompile.sh
/bin/cat <<EOM >${FILE}
#!/bin/bash
cd $BUGPATH
mvn compile
if [ "$?" -ne 0 ]; then
      echo "error compiling defect"
      exit 1
fi
EOM


chmod 777 $BUGPATH/runCompile.sh

#create config file
CONFIGLIBS=$GP4J_HOME"/lib/junittestrunner.jar"
FILE=$BUGPATH/introclass.config
/bin/cat <<EOM >$FILE
seed = 0
sanity = yes
popsize = 6
generations = 5
javaVM = $DIROFJAVA8/jre/bin/java
workingDir = $BUGPATH
outputDir = $BUGPATH/tmp
classSourceFolder = $BUGPATH/target/classes
classTestFolder = $BUGPATH/target/test-classes
libs = ${CONFIGLIBS}
sourceDir = src/main/java
positiveTests = ${POSTESTS}
negativeTests = ${NEGTESTS}
positiveTestClassesDaikonSample = ${POSTESTS}
pathToNoTimeoutTests = ${DAIKONTESTS}
jacocoPath = ${GP4J_HOME}/lib/jacocoagent.jar
testClassPath = ${TESTCP}:${GP4J_HOME}/lib/junit-4.12.jar:${GP4J_HOME}/lib/hamcrest-core-1.3.jar:${GP4J_HOME}/lib/junittestrunner.jar
srcClassPath = ${BUGPATH}/target/classes/
compileCommand = ${BUGPATH}/runCompile.sh
targetClassName = ${BUGPATH}/bugfiles.txt
invariantCheckerMode = $INVCHKMODE
crossp = 1.0

sample = 1.0

testGranularity = method

edits=append;replace;delete

negativePathWeight=0.65
positivePathWeight=0.35
EOM

chmod 777 $BUGPATH/introclass.config


fi
