#!/bin/bash

A=../data/tiny_a.bed
B=../data/tiny_b.bed
C=../data/tiny_c.bed
D=../data/tiny_d.bed

TMP=.tmp.gql

GQL=../gql.py

function run_test {
	echo $1
	echo $2 > $TMP
	R=`$GQL $TMP`
	E=$?
	if [ $E -ne $3 ]
	then
		echo $R
	fi
	rm $TMP
}

run_test "1 ::: LOAD, PRINT" \
	"a = LOAD \"$A\";PRINT a;" \
	0

run_test "2 ::: LOAD AS, COUNT"  \
	"a = LOAD \"$A\" AS BED6;PRINT a;COUNT a;" \
	0

run_test "3 ::: Wrong file type on LOAD" "a = LOAD \"$A\" AS BED3;" \
	0
run_test "4 ::: Wrong file type on LOAD" "a = LOAD \"$A\" AS BED12;" \
	0

run_test "5 ::: Binary INTERSECT, COUNT BEDM" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	c = LOAD \"$C\";
	d = LOAD \"$D\";
	e = a,b INTERSECT a,b,c,d;
	PRINT e;
	COUNT e;" \
	0

run_test "6 ::: Unary INTERSECT, COUNT BEDN" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	c = LOAD \"$C\";
	d = LOAD \"$D\";
	e = INTERSECT a,b,c,d;
	PRINT e;
	COUNT e;" \
	0

run_test "7 ::: SUBTRACT" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	c = LOAD \"$C\";
	e = a SUBTRACT b,c;
	PRINT e;
	COUNT e;" \
	0

run_test "8 ::: MERGEMAX" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	e = MERGEMAX  a,b;
	PRINT e;
	COUNT e;" \
	0

run_test "9 ::: MERGEMAX, DISTANCE" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	e = MERGEMAX a,b WHERE DISTANCE(10);
	PRINT e;
	COUNT e;" \
	0

run_test "10 ::: MERGEMAX, DISTANCE" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	e = MERGEMAX a,b WHERE DISTANCE(50);
	PRINT e;
	COUNT e;" \
	0

run_test "11 ::: MERGEMAX, DISTANCE, SCORE, MIN" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	e = MERGEMAX a,b WHERE DISTANCE(50),SCORE(MIN);
	PRINT e;
	COUNT e;" \
	0

run_test "12 ::: MERGEMAX, DISTANCE, SCORE, MAX" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	c = LOAD \"$C\";
	e = MERGEMAX a,b,c WHERE DISTANCE(50),SCORE(MAX);
	PRINT e;
	COUNT e;" \
	0

run_test "13 ::: MERGEMAX, DISTANCE, SCORE, SUM" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	c = LOAD \"$C\";
	e = MERGEMAX a,b,c WHERE DISTANCE(50),SCORE(SUM);
	PRINT e;" \
	0

run_test "14 ::: MERGEMAX, DISTANCE, SCORE, COUNT" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	c = LOAD \"$C\";
	e = MERGEMAX a,b,c WHERE DISTANCE(50),SCORE(COUNT);
	PRINT e;" \
	0

run_test "15 ::: MERGEMAX, DISTANCE, NAME, SCORE, COUNT" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	c = LOAD \"$C\";
	e = MERGEMAX a,b,c WHERE DISTANCE(50),NAME(COLLAPSE),SCORE(COUNT);
	PRINT e;" \
	0

run_test "16 ::: MERGEFLAT, DISTANCE, NAME, SCORE, COUNT" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	c = LOAD \"$C\";
	e = MERGEFLAT a,b,c WHERE NAME(COLLAPSE),SCORE(COUNT);
	PRINT e;" \
	0
