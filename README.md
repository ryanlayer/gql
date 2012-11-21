Genome Query Language (GQL)
==========================

Test files:

tiny_a.bed

		chr1    1       4       a1      1       +
		chr1    6       8       a2      2       +
		chr1    14      17      a3      3       +
		chr1    500     501     a4      4       +
		chr2    500     501     a4      4       +

Example GQL Programs:

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
