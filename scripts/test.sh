#!/bin/sh

#export BUCKET_SRC=1950census-desc
export BUCKET_SRC=nara-census-jpg-prod-gc
export BUCKET_DST=nara-textract-gc
export REGION=us-gov-east-1
#export DEBUG=debug

#[ -n "$1" ]&&file="$(readlink -e $1)"

path=$(dirname $(readlink -e $0))

python3 "$path/test.py" $@
