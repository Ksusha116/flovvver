#!/bin/bash

awk 'BEGIN {print "Те, у кого балл больше 80"} $2>80'  students.txt
awk 'BEGIN {print "Те, у кого балл меньше 70"} $2<70' students.txt
awk 'BEGIN {print "Первая строка файла"} NR==1' students.txt
