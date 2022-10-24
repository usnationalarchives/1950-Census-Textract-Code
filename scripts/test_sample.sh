#!/bin/sh

path=$(dirname $(readlink -e $0))

if [ -n "$1" ] && [ -f "$1" ]; then
  if [ -n "$2" ]; then
     count=$2
  else
     count=1
  fi
  for image in $(cat $1|grep -e '1[1-9]\.jpg'|head -n $count); do      
      $path/test.sh --debug --s3 $image
  done
else
echo "Error"
fi