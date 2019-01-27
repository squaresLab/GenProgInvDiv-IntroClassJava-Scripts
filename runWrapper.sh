#!/bin/bash

PROJ=$1
STNT=$2
REVN=$3
ICJ=/home/lvyiwei1/bench/IntroClassJava
BGDR=/home/lvyiwei1/bench/
JAVA=/usr/lib/jvm/java-8-openjdk-amd64/
SSED=0
ESED=5
MODE=$4

bash runGenProgForBugIntroclass.sh $PROJ $STNT $REVN $ICJ $BGDR $JAVA $SSED $ESED $MODE
