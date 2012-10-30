import ply.yacc as yacc
from gqltokens import tokens

start = "gql"

precedence = (
		('left', 'EQUALEQUAL'),
		('left', 'PLUS', 'MINUS'),
		('left', 'TIMES', 'DIVIDE'),
)


def p_gql(p):
	'gql : element gql'
	#print "p_gql"
	p[0] = [ p[1] ] + p[2]

def p_gql_empty(p):
	'gql : '
	p[0] = [ ]

def p_element_stmt(p):
	'element : sstmt'
	#print "p_element_stmt"
	p[0] = ("stmt",p.lineno(1),p[1])


def p_stmts(p):
	'stmts : sstmt stmts'
	#print "p_stmts"
	p[0] = [p[1]] + p[2]

def p_stmts_empty(p):
	'stmts : '
	p[0] = [ ]

def p_sstmt_assignment(p):
	'sstmt : IDENTIFIER EQUAL exp SEMICOLON'
	#print "p_sstmt_assignment"
	p[0] = ("assign",p[1],p[3])

def p_sstmt_print(p):
	'sstmt : PRINT ident SEMICOLON'
	p[0] = ("print",  p[2] )

def p_sstmt_save(p):
	'sstmt : SAVE ident AS file SEMICOLON'
	p[0] = ("save",  p[2], p[4] )

def p_sstmt_exp(p):
	'sstmt : exp SEMICOLON'
	#print "p_sstmt_exp"
	p[0] = ("exp",p[1])

def p_exp_identifier(p):
	'exp : IDENTIFIER'
	p[0] = ("identifier",p[1])

def p_exp_number(p):
	'exp : NUMBER'
	p[0] = ("number",p[1])

def p_exp_string(p):
	'exp : STRING'
	p[0] = ("string",p[1])

def p_file(p):
	'file : exp'
	p[0] = ("file", p[1])

def p_filetype(p):
	'filetype : filetypes'
	p[0] = ("filetype", p[1])

def p_filetypes(p):
	'''filetypes : BED3
		| BED6
		| BED12
		| GENOME'''
	p[0] = p[1]

def p_exp_load(p):
	'exp : LOAD file AS filetype'
	#print "p_exp_load"
	p[0] = ("load", p[2], p[4])

def p_exp_intersect(p):
	'exp : INTERSECT idents'
	#print "p_exp_intersect"
	p[0] = ("intersect",  p[2] )

def p_exp_subtract(p):
	'exp : SUBTRACT idents'
	#print "p_exp_intersect"
	p[0] = ("subtract",  p[2] )


def p_idents(p):
	'idents : ident COMMA idents'
	p[0] = [p[1]] + p[3]


def p_idents_one(p):
	'idents : ident'
	p[0] = [p[1]] 

def p_idnent_identifier(p):
	'ident : IDENTIFIER'
	p[0] = ("identifier",p[1])

def p_optargs(p):
	'optargs : args'
	p[0] = p[1]

def p_optargs_empty(p):
	'optargs : '
	p[0] = [ ]

def p_args(p):
	'args : exp COMMA args'
	p[0] = [p[1]] + p[3]

def p_args_one(p):
	'args : exp'
	p[0] = [p[1]] 

# Error rule for syntax errors
def p_error(p):
	print "Syntax error in input. line:" + str(p.lineno) 
