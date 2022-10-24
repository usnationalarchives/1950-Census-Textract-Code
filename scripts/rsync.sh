#!/bin/sh


spath=$(dirname $(readlink -e $0))
path=$(dirname $spath)


rsync -av --delete --exclude=__pycache__ --exclude=tmp --exclude=census --exclude=dependencies \
--exclude=debug --exclude=output --exclude=.git --exclude=.serverless \
--exclude=data/images --exclude=data/images.bak \
--exclude=log \
"$path/" wzhang@10.192.1.232:/appdata2/census/textract/

