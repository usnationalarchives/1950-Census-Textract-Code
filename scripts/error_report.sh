#!/bin/sh

p=$(dirname $(dirname $(readlink -f $0)))

data="$p/data/textract_processed_list.txt"

echo "TIFF Files,JPG Files,Error Log URL"
for line in $(cat $data|awk '/\.txt/ {print $4}'); do
#echo $line
echo "s3://nara-census-prod-gc/$(echo $line|sed 's/\.txt/\.tif/'),s3://ara-census-jpg-prod-gc/$(echo $line|sed 's/\.txt/\.jpg/'),https://nara-textract-gc.s3-us-gov-east-1.amazonaws.com/$line"
done