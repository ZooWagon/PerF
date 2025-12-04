#!/bin/bash
echo "run simulate - msg loss - test-m-100"
echo "min $1, max $2, step $3"

fr=`echo $1 | bc`
# init MLfaultRate as 0.0
sed -i -r 's/MLfaultRate\ :\ [0-9]\.*[0-9]+,/MLfaultRate\ :\ 0\.0,/' ./input-modules/fault-ramp-f.maude
echo "-------"
echo "MLfaultRate=0.0"
sh trans-script/run.sh ramp-f.maude init-ramp-f.maude fault-ramp-f.maude event-ramp-f.maude
sh test-script/fg-test.sh 100 test-m-100

fr=`echo $fr + $3 | bc`
while (($(echo "$fr <= $2" | bc)))
do
    echo "-------"
    echo "MLfaultRate=$fr"
    sed -i -r 's/MLfaultRate\ :\ [0-9]+\.*[0-9]+,/MLfaultRate\ :\ 0'$fr',/' ./input-modules/fault-ramp-f.maude
    sh trans-script/run.sh ramp-f.maude init-ramp-f.maude fault-ramp-f.maude event-ramp-f.maude
    sh test-script/fg-test.sh 100 test-m-100
    fr=`echo $fr + $3 | bc`
done

# substitute 's/a/b/g'
# sed -i 's/MLfaultRate : 0.4/MLfaultRate : 0.3/g' ./input-modules/fault-ramp-f.maude
# sh trans-script/run.sh ramp-f.maude init-ramp-f.maude fault-ramp-f.maude event-ramp-f.maude
# sh test-script/fg-test.sh 100 test-m
