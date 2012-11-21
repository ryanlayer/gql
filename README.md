Example GQL Programs:
=====================

Data sets give at the end.

LOAD, PRINT, COUNT

		a = LOAD "tiny_a.bed";
		PRINT a;
		c=COUNT a;
		PRINT c;

Result

		chr1    1       4       a1      1       +
		chr1    6       8       a2      2       +
		chr1    14      17      a3      3       +
		chr1    500     501     a4      4       +
		chr2    500     501     a4      4       +
		5

Unary INTERSECT

		a = LOAD "../data/tiny_a.bed";
		b = LOAD "../data/tiny_b.bed";
		c = LOAD "../data/tiny_c.bed";
		d = LOAD "../data/tiny_d.bed";
		e = INTERSECT a,b,c,d;
		PRINT e;
		f=COUNT e;
		PRINT f;
	
Result
		chr1	14	17	a3	3	+	chr1	12	16	b3	3	+	chr1	15	18	c3 +	chr1	15	18	d3	3	+ 
		1

Mutlti-file LOAD, Binary INTERSECT

		a = LOAD "tiny_a.bed"; 
		b = LOAD "tiny_b.bed"; 
		c = LOAD "tiny_*.bed";
		e = a,b INTERSECT c;
		PRINT e; 
		f = COUNT e;
		PRINT f;

Result

		a::tiny_a.bed
		chr1	1	4	a1	1	+	chr1	1	4	a1	1	+	3
		chr1	6	8	a2	2	+	chr1	6	8	a2	2	+	2
		chr1	14	17	a3	3	+	chr1	14	17	a3	3	+	3
		chr1	500	501	a4	4	+	chr1	500	501	a4	4	+	1
		chr2	500	501	a4	4	+	chr2	500	501	a4	4	+	1
		a::tiny_b.bed
		chr1	1	4	a1	1	+	chr1	3	7	b1	1	-	1
		chr1	6	8	a2	2	+	chr1	3	7	b1	1	-	1
		chr1	14	17	a3	3	+	chr1	12	16	b3	3	+	2
		a::tiny_c.bed
		chr1	1	4	a1	1	+	chr1	2	5	c1	1	+	2
		chr1	14	17	a3	3	+	chr1	15	18	c3	3	+	2
		a::tiny_d.bed
		chr1	6	8	a2	2	+	chr1	5	8	d1	1	+	2
		chr1	14	17	a3	3	+	chr1	15	18	d3	3	+	2
		b::tiny_a.bed
		chr1	3	7	b1	1	-	chr1	1	4	a1	1	+	1
		chr1	3	7	b1	1	-	chr1	6	8	a2	2	+	1
		chr1	12	16	b3	3	+	chr1	14	17	a3	3	+	2
		b::tiny_b.bed
		chr1	3	7	b1	1	-	chr1	3	7	b1	1	-	4
		chr1	9	11	b2	2	+	chr1	9	11	b2	2	+	2
		chr1	12	16	b3	3	+	chr1	12	16	b3	3	+	4
		chr3	12	16	b3	3	+	chr3	12	16	b3	3	+	4
		b::tiny_c.bed
		chr1	3	7	b1	1	-	chr1	2	5	c1	1	+	2
		chr1	9	11	b2	2	+	chr1	10	13	c2	2	+	1
		chr1	12	16	b3	3	+	chr1	10	13	c2	2	+	1
		chr1	12	16	b3	3	+	chr1	15	18	c3	3	+	1
		b::tiny_d.bed
		chr1	3	7	b1	1	-	chr1	5	8	d1	1	+	2
		chr1	9	11	b2	2	+	chr1	10	13	d2	2	+	1
		chr1	12	16	b3	3	+	chr1	10	13	d2	2	+	1
		chr1	12	16	b3	3	+	chr1	15	18	d3	3	+	1
			tiny_a.bed	tiny_b.bed	tiny_c.bed	tiny_d.bed
		a	5	3	2	2
		b	3	4	4	4

SUBTRACT

		a = LOAD "tiny_a.bed";
		b = LOAD "tiny_b.bed";
		c = LOAD "tiny_c.bed";
		e = a SUBTRACT b,c;
		PRINT e;
		f =COUNT e;
		PRINT f;

Result

		chr1    500     501     a4      4       +
		chr2    500     501     a4      4       +
		2

MERGEMAX

		a = LOAD "../data/tiny_a.bed";
		b = LOAD "../data/tiny_b.bed";
		e = MERGEMAX a,b;
		PRINT e;
		f =COUNT e;
		PRINT f;

Result

		chr1    1       8
		chr1    9       11
		chr1    12      17
		chr1    500     501
		chr2    500     501
		chr3    12      16
		6

MERGEMAX, SCORE,SUM

		a = LOAD "../data/tiny_a.bed";
		b = LOAD "../data/tiny_b.bed";
		e = MERGEMAX a,b WHERE SCORE(SUM);
		PRINT e;
		f = COUNT e;
		PRINT f;

Result

		chr1    1       8       .       4       .
		chr1    9       11      .       2       .
		chr1    12      17      .       6       .
		chr1    500     501     .       4       .
		chr2    500     501     .       4       .
		chr3    12      16      .       3       .
		6

MERGEMAX, SCORE, MEDIAN

		a = LOAD "../data/tiny_a.bed";
		b = LOAD "../data/tiny_b.bed";
		e = MERGEMAX a,b WHERE SCORE(MEDIAN);
		PRINT e;
		f=COUNT e;
		PRINT f;

Result

		chr1    1       8       .       1       .
		chr1    9       11      .       2       .
		chr1    12      17      .       3       .
		chr1    500     501     .       4       .
		chr2    500     501     .       4       .
		chr3    12      16      .       3       .
		6

MERGEFLAT, NAME, SCORE, COUNT

		a = LOAD "../data/tiny_a.bed";
		b = LOAD "../data/tiny_b.bed";
		c = LOAD "../data/tiny_c.bed";
		e = MERGEFLAT a,b,c WHERE NAME(COLLAPSE),SCORE(COUNT);
		PRINT e;

Result

		chr1    1       2       a1      1       .
		chr1    2       3       a1;c1   2       .
		chr1    3       4       a1;b1;c1        3       .
		chr1    4       5       b1;c1   2       .
		chr1    5       6       b1      1       .
		chr1    6       7       b1;a2   2       .
		chr1    7       8       a2      1       .
		chr1    9       10      b2      1       .
		chr1    10      11      c2;b2   2       .
		chr1    11      12      c2      1       .
		chr1    12      13      c2;b3   2       .
		chr1    13      14      b3      1       .
		chr1    14      15      a3;b3   2       .
		chr1    15      16      a3;b3;c3        3       .
		chr1    16      17      a3;c3   2       .
		chr1    17      18      c3      1       .
		chr1    500     501     a4      1       .
		chr2    500     501     a4      1       .
		chr3    12      16      b3      1       .
		chr4    15      18      c3      1       .

MERGEMIN, NAME, SCORE, COUNT

		a = LOAD "../data/tiny_a.bed";
		b = LOAD "../data/tiny_b.bed";
		c = LOAD "../data/tiny_c.bed";
		e = MERGEMIN a,b,c WHERE NAME(COLLAPSE),SCORE(COUNT);
		PRINT e;

Result

		chr1    3       4       a1;b1;c1        3       .
		chr1    6       7       b1;a2   2       .
		chr1    10      11      c2;b2   2       .
		chr1    12      13      c2;b3   2       .
		chr1    15      16      a3;b3;c3        3       .
		chr1    500     501     a4      1       .
		chr2    500     501     a4      1       .
		chr3    12      16      b3      1       .
		chr4    15      18      c3      1       .

MERGEMIN, NAME, SCORE, FILTER

		a = LOAD "../data/tiny_a.bed";
		b = LOAD "../data/tiny_b.bed";
		c = LOAD "../data/tiny_c.bed";
		e = MERGEMIN a,b,c WHERE NAME(COLLAPSE),SCORE(COUNT);
		f = FILTER e WHERE SCORE(>1);
		PRINT f;

Result

		chr1	3	4	a1;b1;c1	3	.
		chr1	6	7	b1;a2	2	.
		chr1	10	11	c2;b2	2	.
		chr1	12	13	c2;b3	2	.
		chr1	15	16	a3;b3;c3	3	.

JACCARD

		a = LOAD "data/tiny_a.bed";
		b = LOAD "data/tiny_b.bed";
		c = LOAD "data/tiny_c.bed";
		d = LOAD "data/tiny_d.bed";
		e = a JACCARD b,c,d;
		PRINT e;

Result

			b	c	d
		a	0.2	0.222222	0.040404


Test files:
===========

tiny_a.bed

		chr1    1       4       a1      1       +
		chr1    6       8       a2      2       +
		chr1    14      17      a3      3       +
		chr1    500     501     a4      4       +
		chr2    500     501     a4      4       +

tiny_b.bed

		chr1	3	7	b1	1	-
		chr1	9	11	b2	2	+
		chr1	12	16	b3	3	+
		chr3	12	16	b3	3	+

tiny_c.bed

		chr1	2	5	c1	1	+
		chr1	10	13	c2	2	+
		chr1	15	18	c3	3	+
		chr4	15	18	c3	3	+
		
tiny_d.bed

		chr1	5	8	d1	1	+
		chr1	10	13	d2	2	+
		chr1	15	18	d3	3	+
		chr1	20	23	d4	4	+
		chr1	25	28	d5	5	+
		chr1	30	33	d6	6	+
		chr1	35	38	d7	7	+
		chr1	40	43	d8	8	+
		chr1	45	48	d9	9	+
		chr1	50	53	d10	10	+
		chr1	55	58	d11	11	+
		chr1	60	63	d12	12	+
		chr1	65	68	d13	13	+
		chr1	70	73	d14	14	+
		chr1	75	78	d15	15	+
		chr1	80	83	d16	16	+
		chr1	85	88	d17	17	+
		chr1	90	93	d18	18	+
		chr1	95	98	d19	19	+
		chr1	100	103	d20	20	+
		chr1	105	108	d21	21	+
		chr1	110	113	d22	22	+
		chr1	115	118	d23	23	+
		chr1	120	123	d24	24	+
		chr1	125	128	d25	25	+
		chr1	130	133	d26	26	+
		chr1	135	138	d27	27	+
		chr1	140	143	d28	28	+
		chr1	145	148	d29	29	+
		chr1	150	153	d30	30	+
		chrX	150	153	d30	30	+


