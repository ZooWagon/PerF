#!/bin/bash
echo "run simulate - delay"
echo "min $1, max $2, step $3"

fr=`echo $1 | bc`
# init delay as 0.0
sed -i -r 's/DEtime\ :\ [0-9]+\.*[0-9]+,/DEtime\ :\ 0\.0,/' ./input-modules/fault-dns.maude
echo "-------"
echo "DEtime = 0.0"
sh trans-script/run.sh dns.maude init-dns.maude fault-dns.maude event-dns.maude
sh test-script/fg-test.sh f-output

fr=`echo $fr + $3 | bc`
while (($(echo "$fr <= $2" | bc)))
do
    echo "-------"
    echo "DEtime=$fr"
    sed -i -r 's/DEtime\ :\ [0-9]+\.*[0-9]+,/DEtime\ :\ '$fr',/' ./input-modules/fault-dns.maude
    sh trans-script/run.sh dns.maude init-dns.maude fault-dns.maude event-dns.maude
    sh test-script/fg-test.sh f-output
    fr=`echo $fr + $3 | bc`
done

# substitute 's/a/b/g'
# sed -i 's/DEtime : 200.0/DEtime : 300.0/g' ./input-modules/fault-dns.maude
# sh trans-script/run.sh dns.maude init-dns.maude fault-dns.maude event-dns.maude
# sh test-script/fg-test.sh f-output
