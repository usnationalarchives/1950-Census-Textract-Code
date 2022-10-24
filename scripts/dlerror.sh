#!/bin/bash

text_bucket=nara-textract
image_bucket=nara-census-prod


if [[ -z $1 || -z $2 ]]; then
    echo "USAGE:"
    echo "   dlerror.sh listfile.txt /download/path"
    exit 1
fi

list=$1
path=$(readlink -e $2)

for file in $(cat "$list"|awk '/\.txt$/ {print $4}'); do
    aws s3 cp "s3://$text_bucket/$file" "$path/"
    img=$(echo $file|sed -r 's/\.txt$/.jpg/')
    aws s3 cp "s3://$image_bucket/$img" "$path/"
done    