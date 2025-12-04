#!/bin/bash
echo ">> Sim Testing test-m <<"

timestamp1=$(date +%s.%3N)
python test-script/fg-gene-input.py
timestamp2=$(date +%s.%3N)

echo -n "Input generated. Running ..." 
timestamp3=$(date +%s.%3N)
maude < test-script/fg-input.txt > test-script/fg.log
timestamp4=$(date +%s.%3N)
echo "Analyzing ..."
timestamp5=$(date +%s.%3N)
python test-script/fg-analyze.py
timestamp6=$(date +%s.%3N)

echo -n "Used time(seconds):"
echo "$timestamp1 $timestamp6" | awk '{printf "%.3f\n", $2-$1}'
# echo -n "Input genearted:" 
# echo "$timestamp1 $timestamp2" | awk '{printf "%.3f\n", $2-$1}'
# echo -n "Maude run:" 
# echo "$timestamp3 $timestamp4" | awk '{printf "%.3f\n", $2-$1}'
# echo -n "Analysis:" 
# echo "$timestamp5 $timestamp6" | awk '{printf "%.3f\n", $2-$1}'