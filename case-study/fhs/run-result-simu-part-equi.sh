#!/bin/bash
echo "run simulate - fhs - partition + equivocation"
echo "node number 16, evil node from 0 to 5"

en=0
while ((en<6))
do
    echo "-------"
    echo "equivocate node num = $en"
    sh trans-script/run.sh fhs.maude init-fhs.maude fault-fhs-co16-$en.maude event-fhs.maude
    sh test-script/fg-test.sh
    ((en++))
done

