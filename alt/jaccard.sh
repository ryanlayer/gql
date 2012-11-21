#!/bin/bash

A=../data/tiny_a.bed
B=../data/tiny_b.bed
C=../data/tiny_c.bed

A_SORT=../data/tiny_a_sorted.bed
B_SORT=../data/tiny_b_sorted.bed
C_SORT=../data/tiny_c_sorted.bed

bedtools sort -i $A > $A_SORT
bedtools sort -i $B > $B_SORT
bedtools sort -i $C > $C_SORT

bedtools jaccard -a $A_SORT -b $B_SORT
bedtools jaccard -a $A_SORT -b $C_SORT
bedtools jaccard -a $B_SORT -b $C_SORT

echo "pybedtools"
python - <<END
import pybedtools
pybedtools.settings.KEEP_TEMPFILES=True
sorted_a = pybedtools.BedTool('$A').sort()
sorted_b = pybedtools.BedTool('$B').sort()
sorted_c = pybedtools.BedTool('$C').sort()

r = sorted_a.jaccard(b=sorted_b)
print r

r = sorted_a.jaccard(b=sorted_c)
print r

r = sorted_b.jaccard(b=sorted_c)
print r

END
