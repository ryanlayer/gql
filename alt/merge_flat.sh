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

echo "bedtools multiinter -i $A_SORT $B_SORT $C_SORT -gql"
bedtools multiinter -i $A_SORT $B_SORT $C_SORT -gql
echo "bedtools multiinter -i $A_SORT $B_SORT $C_SORT -gql -scores sum "
bedtools multiinter -i $A_SORT $B_SORT $C_SORT -gql -scores sum 
echo "bedtools multiinter -i $A_SORT $B_SORT $C_SORT -gql -nms"
bedtools multiinter -i $A_SORT $B_SORT $C_SORT -gql -nms
echo "bedtools multiinter -i $A_SORT $B_SORT $C_SORT -gql -scores sum -nms"
bedtools multiinter -i $A_SORT $B_SORT $C_SORT -gql -scores sum -nms

echo "pybedtools"
python - <<END
import pybedtools
sorted_a = pybedtools.BedTool('$A').sort()
sorted_b = pybedtools.BedTool('$B').sort()
sorted_c = pybedtools.BedTool('$C').sort()

r = sorted_a.multi_intersect(i=[sorted_b.fn, sorted_c.fn],\
	gql=True)
print r

r = sorted_a.multi_intersect(i=[sorted_b.fn, sorted_c.fn],\
	gql=True,\
	scores='sum')
print r

r = sorted_a.multi_intersect(i=[sorted_b.fn, sorted_c.fn],\
	gql=True,\
	nms=True)
print r

r = sorted_a.multi_intersect(i=[sorted_b.fn, sorted_c.fn],\
	gql=True,\
	scores='sum',\
	nms=True)
print r

END
