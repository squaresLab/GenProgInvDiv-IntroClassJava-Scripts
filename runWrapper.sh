#!/bin/bash

LABBOX=/Users/zhendeveloper/Desktop/LabBox

PROJ=$1
STNT=$2
REVN=$3
ICJ=$LABBOX/IntroClassJava
BGDR=$LABBOX/ProgRepScripts/ICSTest
JAVA=/Library/Java/JavaVirtualMachines/jdk1.8.0_45.jdk/Contents/Home/
SSED=0
ESED=5
MODE=$4

bash runGenProgForBugIntroclass.sh $PROJ $STNT $REVN $ICJ $BGDR $JAVA $SSED $ESED $MODE