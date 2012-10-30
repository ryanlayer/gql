import ply.lex as lex
import gqltokens

gql_lexer = lex.lex(module=gqltokens)

data='''
# test load
hg19 = LOAD "file0" AS GENOME;
a = LOAD "file1" AS BED3 GENOME hg19;
b = LOAD "file2" AS BED3 GENOME hg19;

# test intersect
c = INTERSECT a,b;
'''

gql_lexer.input(data)
while True:
	tok = gql_lexer.token()
	if not tok:
		break
	print tok
