#!/bin/bash

A=../data/a.bed
B=../data/b.bed
C=../data/c.bed
D=../data/d.bed

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
