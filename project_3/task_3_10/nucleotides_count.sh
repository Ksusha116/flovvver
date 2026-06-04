#!/bin/bash


printf "%-15s %-7s %-7s %-7s %-7s\n" "Файл" "A" "T" "G" "C"

for file in *.fasta; do
    if [ ! -s "$file" ]; then
        continue
    fi

    sequence=$(grep -v "^>" "$file" | tr -d '\n')

    a_count=$(echo "$sequence" | grep -o "A" | wc -l)
    t_count=$(echo "$sequence" | grep -o "T" | wc -l)
    g_count=$(echo "$sequence" | grep -o "G" | wc -l)
    c_count=$(echo "$sequence" | grep -o "C" | wc -l)
    printf "%-15s %-7d %-7d %-7d %-7d\n" "$file" "$a_count" "$t_count" "$g_count" "$c_count"
done
