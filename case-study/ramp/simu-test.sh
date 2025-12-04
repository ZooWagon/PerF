#!/bin/bash
# echo "run simulate"
# echo "min $1, max $2, step $3"

# fr=`echo $1 | bc`
# lfr=$1

# # lfr=$fr
# # fr=`echo $fr + $3 | bc`

# echo "MLfaultRate=$fr"
sed -i -r 's/MLfaultRate\ :\ [0-9]\.*[0-9]+,/MLfaultRate\ :\ 0\.0,/' ./input-modules/fault-ramp-f.maude
# sh trans-script/run.sh ramp-f.maude init-ramp-f.maude fault-ramp-f.maude event-ramp-f.maude
# sh test-script/fg-test.sh 100 test-m