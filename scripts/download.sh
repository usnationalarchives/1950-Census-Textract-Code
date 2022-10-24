#!/bin/bash

state=$1
num=$2

if [ -z "$state" ]; then
  echo "Need state name"
  exit
fi



spath=$(dirname $(readlink -e $0))
path=$(dirname $spath)

i=0
for img in $(grep "${state}.*\.jpg" $path/data/1950desc.txt); do
(( i = i + 1 ))
aws s3 cp s3://1950census-desc/$img $path/data/images/

if [[ -n $num  && "$i" -ge "$num" ]]; then
   break
fi
done