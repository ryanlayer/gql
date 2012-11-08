
A=../data/tiny_a.bed
B=../data/tiny_b.bed
C=../data/tiny_c.bed
ABC=../data/tiny_abc.bed
ABC_SORT=../data/tiny_abc_sorted.bed

cat $A $B $C > $ABC
bedtools sort -i $ABC > $ABC_SORT
echo "bedtools merge -i $ABC_SORT"
bedtools merge -i $ABC_SORT
echo "bedtools merge -i $ABC_SORT -nms"
bedtools merge -i $ABC_SORT -nms
echo "bedtools merge -i $ABC_SORT -scores count"
bedtools merge -i $ABC_SORT -scores count
echo "bedtools merge -i $ABC_SORT -s"
bedtools merge -i $ABC_SORT -s

echo "pybedtools"
python - <<END
import pybedtools
sorted_bed = pybedtools.BedTool('$ABC').sort()
c = sorted_bed.merge()
print c
c = sorted_bed.merge(nms=True)
print c
c = sorted_bed.merge(scores='count')
print c
c = sorted_bed.merge(s=True)
print c
c = sorted_bed.merge(d=50, scores='count')
print c
c = sorted_bed.merge(d=50, scores='count')
print c
END
