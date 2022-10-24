#!/bin/sh
path=$(dirname $(dirname $(readlink -e $0)))

#export VIRTUAL_ENV="$path/dependencies/python"
#python3 -m venv $path/dependencies/python && . $path/dependencies/python/bin/activate && \
#python3 -m pip install boto3 pillow sagemaker opencv-python editdistance && \
[ -d "$path/dependencies" ]&&rm -rf "$path/dependencies"

python3 -m venv $path/dependencies && . $path/dependencies/bin/activate && \
python3 -m pip install boto3 pillow sagemaker editdistance fuzzywuzzy python-Levenshtein && \
find $path/dependencies -type d -name "tests" -exec rm -rfv "{}" \; && \
find $path/dependencies -type d -name "__pycache__" -exec rm -rfv "{}" \;

libs=$(find "$path/dependencies/lib" -type d -name 'site-packages')

if [ -n "$libs" ]; then
ln -s $libs "$path/dependencies/python"
fi

#du -h $path/dependencies
cd $path/dependencies && zip -r ../dependencies.zip python

echo "VIRTUAL_ENV=$VIRTUAL_ENV"