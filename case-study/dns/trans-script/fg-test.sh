#!/bin/bash
echo ">> Sim Testing " $2 " <<"

timestamp1=$(date +%s.%3N)
python trans-script/fg-gene-input.py $1 $2
timestamp2=$(date +%s.%3N)

echo -n "Input generated. Running " 
echo -n $1 
echo " times ..."

timestamp3=$(date +%s.%3N)
maude < trans-script/fg-input.txt > trans-script/fg.log
timestamp4=$(date +%s.%3N)
echo "Analyzing ..."
timestamp5=$(date +%s.%3N)
python trans-script/fg-analyze.py $1
timestamp6=$(date +%s.%3N)

echo -n "Used time(seconds):"
echo "$timestamp1 $timestamp6" | awk '{printf "%.3f\n", $2-$1}'
echo -n "Input genearted:" 
echo "$timestamp1 $timestamp2" | awk '{printf "%.3f\n", $2-$1}'
echo -n "Maude run:" 
echo "$timestamp3 $timestamp4" | awk '{printf "%.3f\n", $2-$1}'
echo -n "Analysis:" 
echo "$timestamp5 $timestamp6" | awk '{printf "%.3f\n", $2-$1}'