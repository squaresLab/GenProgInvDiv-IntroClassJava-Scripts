#!/bin/bash

#The purpose of this script is to run Zhen & Yiwei's diversity-enhancing GenProg for a particular IntroClass bug.

#Preconditions
#The variable GP4J_HOME should be directed to the folder where genprog4java is installed.
#The variable DAIKONDIR should be directed to the folder where daikon is installed

if [ "$#" -ne 9 ]; then
    echo "This script should be run with 9 parameters:"
    echo "1st param is the project in lowercase (e.g: checksum, digits, grade, ...)"
    echo "2nd param is the user id, located in the directories of projects (e.g: 2c1556672751734adf9a561fbf88767c...)"
    echo "3rd param is the revision number, located in the directories of user ids (e.g: 003)"
    echo "4th param is the path to IntroClassJava (containing dataset/, lib/, and README.md)"
    echo "5th param is the path to a directory to copy buggy programs into. GP4J will work with the bug in this directory"
    echo "6th param is the java8 installation"
    echo "7th param is the starting seed"
    echo "8th param is the ending seed (inclusive)"
    echo "9th param is the mode number, indicating which search strategy to use (0 for genprog, 4 for diversity)"

else

PROJECT=$1
USERID=$2
REVID=$3
INTROCLASS=$4
GP4JBUGSDIR=$5
DIROFJAVA8=$6
STARTSEED=$7
ENDSEED=$8
INVCHKMODE=$9

export JAVA_HOME=$DIROFJAVA8
export JRE_HOME=$DIROFJAVA8/jre
export PATH=$DIROFJAVA8/bin/:$PATH

ORIGBUGPATH="$INTROCLASS/dataset/$PROJECT/$USERID/$REVID"

#copy bug from the ORIGBUGPATH in INTROCLASS to the GP4JBUGDIR
BUGWD="$GP4JBUGSDIR/mode$INVCHKMODE/$PROJECT/$USERID/$REVID/"
mkdir -p $BUGWD #make all directories needed
#rm -r $BUGWD/* #clean up directory if needed

echo "NOT compiling gp4j! Remember to compile gp4j manually!"

if [ ! -f $BUGWD/introclass.config ]; then #if preparations aren't already done
    rm -r $BUGWD/* #cleanup directory if there's anything in it.
    rsync -r $ORIGBUGPATH/ $BUGWD
    bash prepareGenProgForBugIntroclass.sh $BUGWD $DIROFJAVA8 $INVCHKMODE
else
    echo "Not running prepareGenProgForBugIntroclass.sh"
fi

cd $BUGWD

for (( seed=$STARTSEED; seed<=$ENDSEED; seed++ )) do
    if [ -f $BUGWD/ResultOfSeed${seed}.results ]; then
        echo "RESULTS FILE DETECTED, NOT RUNNING SEED: $seed "
    else
        echo -n "RUNNING THE BUG: $PROJECT $USERID $REVID, WITH THE SEED: $seed "
        date

        #change the seed
        CHANGESEEDCMD="sed -i.sedtemp '1 s/.*/seed = ${seed}/' introclass.config"
        eval $CHANGESEEDCMD
        rm introclass.config.sedtemp

        if [ $seed != $STARTSEED ]; then
            #remove sanity checking
            REMOVESANITYCMD="sed -i.sedtemp 's/sanity = yes/sanity = no/' introclass.config"
            eval $REMOVESANITYCMD
            rm introclass.config.sedtemp
        fi

        #run w/ 4 hour timeout
        JAVALOC=$(which java)
        timeout 14400 $JAVALOC -ea -Dlog4j.configurationFile=file:"$GP4J_HOME"/src/log4j.properties -Dfile.encoding=UTF-8 -classpath "$GP4J_HOME"/target/uber-GenProg4Java-0.0.1-SNAPSHOT.jar clegoues.genprog4java.main.Main $GP4J_HOME $DIROFJAVA8 $DAIKONDIR $BUGWD/introclass.config | tee $BUGWD/logSeed${seed}.txt

        #save variants in a tar file
        tar -cvf $BUGWD/variantsSeed${seed}.tar $BUGWD/tmp/ > /dev/null
        mv $BUGWD/tmp/original/ $BUGWD
        rm -r $BUGWD/tmp/
        mkdir $BUGWD/tmp/
        mv $BUGWD/original/ $BUGWD/tmp/
        #rm $BUGWD/*.ser
    fi
done

echo -n "End of experiment: "
date

fi
