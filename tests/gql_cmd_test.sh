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
	cat $TMP
	$GQL $TMP
	echo $?
	echo
	rm $TMP
}

run_test "::: LOAD, PRINT"  "a = LOAD \"$A\";PRINT a;"

run_test "::: LOAD AS, COUNT"  \
	"a = LOAD \"$A\" AS BED6;PRINT a;COUNT a;"

run_test "::: Wrong file type on LOAD" "a = LOAD \"$A\" AS BED3;"
run_test "::: Wrong file type on LOAD" "a = LOAD \"$A\" AS BED12;"

run_test "::: Binary INTERSECT, COUNT BEDM" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	c = LOAD \"$C\";
	d = LOAD \"$D\";
	e = a,b INTERSECT a,b,c,d;
	PRINT e;
	COUNT e;"

run_test "::: Unary INTERSECT, COUNT BEDN" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	c = LOAD \"$C\";
	d = LOAD \"$D\";
	e = INTERSECT a,b,c,d;
	PRINT e;
	COUNT e;"

run_test "::: SUBTRACT" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	e = SUBTRACT a,b;
	PRINT e;
	COUNT e;"

run_test "::: MERGE" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	e = MERGE a,b;
	PRINT e;
	COUNT e;"

run_test "::: MERGE, DISTANCE" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	e = MERGE a,b WHERE DISTANCE(10);
	PRINT e;
	COUNT e;"

run_test "::: MERGE, DISTANCE" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	e = MERGE a,b WHERE DISTANCE(50);
	PRINT e;
	COUNT e;"

run_test "::: MERGE, DISTANCE, SCORE, MIN" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	e = MERGE a,b WHERE DISTANCE(50),SCORE(MIN);
	PRINT e;
	COUNT e;"

run_test "::: MERGE, DISTANCE, SCORE, MAX" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	c = LOAD \"$C\";
	e = MERGE a,b,c WHERE DISTANCE(50),SCORE(MAX);
	PRINT e;
	COUNT e;"

run_test "::: MERGE, DISTANCE, SCORE, SUM" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	c = LOAD \"$C\";
	e = MERGE a,b,c WHERE DISTANCE(50),SCORE(SUM);
	PRINT e;"

run_test "::: MERGE, DISTANCE, SCORE, COUNT" \
	"a = LOAD \"$A\";
	b = LOAD \"$B\";
	c = LOAD \"$C\";
	e = MERGE a,b,c WHERE DISTANCE(50),SCORE(COUNT);
	PRINT e;"
