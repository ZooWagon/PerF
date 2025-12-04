#!/bin/bash
echo "run simulate - quorum - partition"
echo "3 server 4 client, partition duration time from 0 to 25 step 5"

pd=0
while ((pd<=25))
do
    echo "-------"
    echo "partition duration time = $pd"
    sh trans-script/run.sh quorum.maude init-quorum.maude fault-quorum-pa-$pd.maude event-quorum.maude
    sh test-script/fg-test.sh
    pd=$((pd+5))
done

