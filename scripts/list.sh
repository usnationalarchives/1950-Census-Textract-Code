#!/bin/sh

p=$(dirname $(dirname $(readlink -f $0)))

output="$p/data/schedule_list"

[ ! -d "$output" ]&&mkdir "$output"

for state in $( aws s3 ls s3://nara-census-prod/census/census-1940/T627/|awk '/PRE/ {print $2}'|grep -v 'XML'|sed -r 's/\/$//'); do
    for img in $(aws s3 ls --recursive s3://nara-census-prod/census/census-1940/T627/$state/|awk '/\.jpg/ {print $4}'|head -n300|tail -n100 2>/dev/null); do
        echo "$img" >> "$output/${state}.txt"
    done
done