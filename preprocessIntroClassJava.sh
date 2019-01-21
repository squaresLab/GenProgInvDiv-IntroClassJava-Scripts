#!/bin/bash

#Put this in the IntroClassJava directory,
#and run it to shorten directory names and get rid of ref/

#truncate to 4 characters
if [ "$#" -ne 1 ]; then
    echo "1st param: path to IntroClassJava"
else

cd $1

PROJECTS=($(ls -d dataset/*/))

BASEDIR=$PWD

for proj in "${PROJECTS[@]}"
do
  cd $BASEDIR/$proj
  rm -r ref/
  STUDENTS=($(ls -d */))
  for student in "${STUDENTS[@]}"
  do
    SHORTNAME=$(echo -n $student | awk '{print substr($1,1,4)}')
    mv $student $SHORTNAME
  done
done
fi