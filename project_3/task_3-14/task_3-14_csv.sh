#!/bin/bash

awk -F "," 'BEGIN {print "Название товаров"} {print $2}' data.csv
awk -F "," 'BEGIN {print "Название товаров дороже 20"} $3>20 {print $2}' data.csv
awk -F "," '{sum+=$3} END {print "Общая сумма " sum}' data.csv
