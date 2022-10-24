spath=$(dirname $(readlink -e $0))
path=$(dirname $spath)

cd "$path"

./scripts/test.sh data/1950census/North_Dakota.txt
./scripts/test.sh data/1950census/Ohio.txt
./scripts/test.sh data/1950census/Oklahoma.txt
./scripts/test.sh data/1950census/Oregon.txt
./scripts/test.sh data/1950census/Panama_Canal.txt
./scripts/test.sh data/1950census/Pennsylvania.txt
./scripts/test.sh data/1950census/Puerto_Rico.txt
./scripts/test.sh data/1950census/Rhode_Island.txt
./scripts/test.sh data/1950census/South_Carolina.txt
./scripts/test.sh data/1950census/South_Dakota.txt
./scripts/test.sh data/1950census/Tennessee.txt
./scripts/test.sh data/1950census/Texas.txt
./scripts/test.sh data/1950census/Utah.txt
./scripts/test.sh data/1950census/Vermont.txt
./scripts/test.sh data/1950census/Virginia.txt
./scripts/test.sh data/1950census/Virgin_Islands.txt
./scripts/test.sh data/1950census/Washington.txt
./scripts/test.sh data/1950census/West_Virginia.txt
./scripts/test.sh data/1950census/Wisconsin.txt
./scripts/test.sh data/1950census/Wyoming.txt
