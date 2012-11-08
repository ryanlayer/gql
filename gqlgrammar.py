import ply.yacc as yacc
from gqltokens import tokens

start = "gql"

#precedence = (
		#('left', 'EQUALEQUAL'),
		#('left', 'PLUS', 'MINUS'),
		#('left', 'TIMES', 'DIVIDE'),
#)


def p_gql(p):
	'gql : element gql'
	p[0] = [ p[1] ] + p[2]

def p_gql_empty(p):
	'gql : '
	p[0] = [ ]

def p_element_stmt(p):
	'element : sstmt'
	p[0] = ("stmt",p.lineno(1),p[1])

#def p_stmts(p):
#	'stmts : sstmt stmts'
#	#print "p_stmts"
#	p[0] = [p[1]] + p[2]
#
#def p_stmts_empty(p):
#	'stmts : '
#	p[0] = [ ]

def p_sstmt_assignment(p):
	'sstmt : IDENTIFIER EQUAL exp SEMICOLON'
	p[0] = ("assign",p[1],p[3])

def p_sstmt_count(p):
	'sstmt : COUNT ident SEMICOLON'
	p[0] = ("count",  p[2] )

def p_sstmt_print(p):
	'sstmt : PRINT ident SEMICOLON'
	p[0] = ("print",  p[2] )

def p_sstmt_save(p):
	'sstmt : SAVE ident AS file SEMICOLON'
	p[0] = ("save",  p[2], p[4] )

def p_sstmt_exp(p):
	'sstmt : exp SEMICOLON'
	p[0] = ("exp",p[1])

def p_exp_identifier(p):
	'exp : IDENTIFIER'
	p[0] = ("identifier",p[1])

def p_exp_number(p):
	'exp : NUMBER'
	p[0] = ("number",p[1])

def p_number_number(p):
	'number : NUMBER'
	p[0] = ("number",p[1])


def p_exp_string(p):
	'exp : STRING'
	p[0] = ("string",p[1])

def p_file(p):
	'file : exp'
	p[0] = ("file", p[1])

def p_optfiletype(p):
	'optfiletype : AS filetype'
	p[0] = p[2]

def p_optfiletype_empty(p):
	'optfiletype : '
	p[0] = ("filetype", "auto")

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
	'exp : LOAD file optfiletype'
	p[0] = ("load", p[2], p[3])

#def p_exp_load_as(p):
#	'exp : LOAD file AS filetype'
#	p[0] = ("load", p[2], p[3])

def p_exp_binary_intersect(p):
	'exp : idents INTERSECT idents'
	p[0] = ("binary-intersect",  p[1], p[3] )

def p_exp_unary_intersect(p):
	'exp : INTERSECT idents'
	p[0] = ("unary-intersect",  p[2] )

def p_exp_subtract(p):
	'exp : ident SUBTRACT idents'
	p[0] = ("subtract",  p[1], p[3] )

def p_exp_merge_min(p):
	'exp : MERGEMIN idents optmods'
	p[0] = ("merge", "min",  p[2], p[3] )

def p_exp_merge_flat(p):
	'exp : MERGEFLAT idents optmods'
	p[0] = ("merge", "flat",  p[2], p[3] )

def p_exp_merge_max(p):
	'exp : MERGEMAX idents optmods'
	p[0] = ("merge", "max", p[2], p[3] )

def p_exp_CAST(p):
	'exp : CAST ident AS filetype optmods'
	p[0] = ("cast", p[2], p[4], p[5] )

def p_exp_optmods(p):
	'optmods : WHERE mods'
	p[0] = p[2]

def p_exp_optmods_empty(p):
	'optmods : '
	p[0] = []

def p_exp_mods(p):
	'mods : mod COMMA mods'
	p[0] = [ p[1] ] +  p[3] 

def p_exp_mods_one(p):
	'mods : mod'
	p[0] = [ p[1] ]

def p_exp_mod(p):
	'''mod : distance
		| score
		| name'''
	p[0] =  p[1]

def p_name(p):
	'name : NAME LPAREN function RPAREN'
	p[0] = ("name", p[3])


def p_distance(p):
	'distance : DISTANCE LPAREN number RPAREN'
	p[0] = ("distance", p[3])

def p_score(p):
	'score : SCORE LPAREN function RPAREN'
	p[0] = ("score", p[3])

def p_function(p):
	'''function : MIN
			| MAX
			| SUM
			| COUNT
			| MEAN
			| MEDIAN
			| MODE
			| ANTIMODE
			| COLLAPSE  
			| STDEV'''
	p[0] = ("function", p[1])

#def p_optidents(p):
#	'optidents : idents'
#	p[0] = p[1]
#
#def p_optidents_empty(p):
#	'optidents : '
#	p[0] = []

def p_idents(p):
	'idents : ident COMMA idents'
	p[0] = [p[1]] + p[3]


def p_idents_one(p):
	'idents : ident'
	p[0] = [p[1]] 

def p_idnent_identifier(p):
	'ident : IDENTIFIER'
	p[0] = ("identifier",p[1])

# Error rule for syntax errors
def p_error(p):
	print "Syntax error in input. line:" + str(p.lineno) 
