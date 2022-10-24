spath=$(dirname $(readlink -e $0))
path=$(dirname $spath)

cd "$path"


./scripts/test.sh data/1950census/Alabama.txt
./scripts/test.sh data/1950census/Alaska.txt
./scripts/test.sh data/1950census/American_Samoa.txt
./scripts/test.sh data/1950census/Arizona.txt
./scripts/test.sh data/1950census/Arkansas.txt
./scripts/test.sh data/1950census/California.txt
./scripts/test.sh data/1950census/Colorado.txt
./scripts/test.sh data/1950census/Connecticut.txt
./scripts/test.sh data/1950census/Delaware.txt
./scripts/test.sh data/1950census/District_of_Columbia.txt
./scripts/test.sh data/1950census/Florida.txt
./scripts/test.sh data/1950census/Georgia.txt
./scripts/test.sh data/1950census/Guam.txt
./scripts/test.sh data/1950census/Hawaii.txt
./scripts/test.sh data/1950census/Idaho.txt
./scripts/test.sh data/1950census/Illinois.txt
