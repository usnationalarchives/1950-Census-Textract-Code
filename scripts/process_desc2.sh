spath=$(dirname $(readlink -e $0))
path=$(dirname $spath)

cd "$path"

./scripts/test.sh data/1950census/Indiana.txt
./scripts/test.sh data/1950census/Iowa.txt
./scripts/test.sh data/1950census/Kansas.txt
./scripts/test.sh data/1950census/Kentucky.txt
./scripts/test.sh data/1950census/Louisiana.txt
./scripts/test.sh data/1950census/Maine.txt
./scripts/test.sh data/1950census/Maryland.txt
./scripts/test.sh data/1950census/Massachusetts.txt
./scripts/test.sh data/1950census/Michigan.txt
./scripts/test.sh data/1950census/Minnesota.txt
./scripts/test.sh data/1950census/Mississippi.txt
./scripts/test.sh data/1950census/Missouri.txt
./scripts/test.sh data/1950census/Montana.txt
./scripts/test.sh data/1950census/Nebraska.txt
./scripts/test.sh data/1950census/Nevada.txt
./scripts/test.sh data/1950census/New_Hampshire.txt
./scripts/test.sh data/1950census/New_Jersey.txt
./scripts/test.sh data/1950census/New_Mexico.txt
./scripts/test.sh data/1950census/New_York.txt
./scripts/test.sh data/1950census/North_Carolina.txt
