import ply.lex as lex
import ply.yacc as yacc
import gqltokens
import gqlgrammar

gql_lexer = lex.lex(module=gqltokens)

data='''
# test load
hg19 = LOAD "file0" AS GENOME;
a = LOAD "file1" AS BED3;
b = LOAD "file2" AS BED3;

# test intersect
c = INTERSECT a,b;
'''

gql_lexer.input(data)
while True:
	tok = gql_lexer.token()
	if not tok:
		break
	print tok

gql_parser = yacc.yacc(module=gqlgrammar,tabmodule="parsetabgql")
gql_ast = gql_parser.parse(data,lexer=gql_lexer,tracking=True)

for elt in gql_ast:
	print elt
