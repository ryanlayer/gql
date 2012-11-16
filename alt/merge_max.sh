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

echo "bedtools multiinter -merge -i $A_SORT $B_SORT $C_SORT -gql"
bedtools multiinter -merge -i $A_SORT $B_SORT $C_SORT -gql
echo "bedtools multiinter -merge -i $A_SORT $B_SORT $C_SORT -gql -scores sum "
bedtools multiinter -merge -i $A_SORT $B_SORT $C_SORT -gql -scores sum 
echo "bedtools multiinter -merge -i $A_SORT $B_SORT $C_SORT -gql -nms"
bedtools multiinter -merge -i $A_SORT $B_SORT $C_SORT -gql -nms
echo "bedtools multiinter -merge -i $A_SORT $B_SORT $C_SORT -gql -scores sum -nms"
bedtools multiinter -merge -i $A_SORT $B_SORT $C_SORT -gql -scores sum -nms

#echo "pybedtools"
#python - <<END
#import pybedtools
#pybedtools.settings.KEEP_TEMPFILES=True
##sorted_a = pybedtools.BedTool('$A').sort()
##sorted_b = pybedtools.BedTool('$B').sort()
##sorted_c = pybedtools.BedTool('$C').sort()
#sorted_a = pybedtools.BedTool('$A').sort()
#sorted_b = pybedtools.BedTool('$B').sort()
#sorted_c = pybedtools.BedTool('$C').sort()
#
#r = sorted_a.multi_intersect(i=[sorted_b.fn, sorted_c.fn],\
#	gql=True,\
#	cluster=True)
#print r
#
#r = sorted_a.multi_intersect(i=[sorted_b.fn, sorted_c.fn],\
#	gql=True,\
#	cluster=True,\
#	scores='sum')
#print r
#
#r = sorted_a.multi_intersect(i=[sorted_b.fn, sorted_c.fn],\
#	gql=True,\
#	cluster=True,\
#	nms=True)
#print r
#
#r = sorted_a.multi_intersect(i=[sorted_b.fn, sorted_c.fn],\
#	gql=True,\
#	cluster=True,\
#	scores='sum',\
#	nms=True)
#print r
#
#END
