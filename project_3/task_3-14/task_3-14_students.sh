#!/bin/bash

awk '{print $1} BEGIN {print "Только имена"}' students.txt
awk '{print $2} BEGIN {print "Только оценки"}' students.txt
awk '{print NR " " $1} BEGIN {print "Номер строки и имя"}' students.txt
