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
	'element : sstmt SEMICOLON'
	p[0] = ("stmt",p.lineno(1),p[1])

#def p_element_no_semicolon(p):
#	'element : sstmt '
#	print 'Missing ";"'
#	p[0] = None
#	p.parser.error = 1

def p_sstmt_assignment(p):
	'sstmt : IDENTIFIER EQUAL exp'
	p[0] = ("assign",p[1],p[3])

def p_sstmt_assignment_error(p):
	'sstmt : IDENTIFIER EQUAL error'
	print 'Invalid assignment.'
	p[0] = None
	p.parser.error = 1


def p_sstmt_print(p):
	'sstmt : PRINT ident'
	p[0] = ("print",  p[2] )

def p_sstmt_peak(p):
	'sstmt : PEAK ident NUMBER'
	p[0] = ("peak",  p[2], p[3])

def p_sstmt_save(p):
	'sstmt : SAVE ident AS file'
	p[0] = ("save",  p[2], p[4] )

def p_sstmt_plot(p):
	'sstmt : PLOT ident AS file'
	p[0] = ("plot",  p[2], p[4] )

def p_sstmt_exp(p):
	'sstmt : exp '
	print 'Invalid statement.'
	p[0] = None

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
		| BED4
		| BED6
		| BED12
		| GENOME'''
	p[0] = p[1]

def p_exp_complement_g(p):
	'exp : COMPLEMENT ident AS ident'
	p[0] = ("complement", p[2], p[4])

def p_exp_complement_genome(p):
	'exp : COMPLEMENT ident AS STRING'
	p[0] = ("complement", p[2], p[4])

def p_exp_sort(p):
	'exp : SORT ident '
	p[0] = ("sort", p[2])

def p_exp_load(p):
	'exp : LOAD file optfiletype'
	p[0] = ("load", p[2], p[3])

def p_exp_foreach(p):
	'exp : FILTER idents optmods'
	p[0] = ("filter", p[2], p[3])

def p_exp_binary_intersect(p):
	'exp : idents INTERSECT idents'
	p[0] = ("binary-intersect",  p[1], p[3] )

def p_exp_binary_jaccard(p):
	'exp : idents JACCARD idents'
	p[0] = ("binary-jaccard",  p[1], p[3] )

def p_exp_unary_intersect(p):
	'exp : INTERSECT idents'
	p[0] = ("unary-intersect",  p[2] )

def p_exp_count(p):
	'exp : COUNT ident'
	p[0] = ("count",  p[2] )

def p_exp_subtract(p):
	'exp : ident SUBTRACT idents'
	p[0] = ("subtract",  p[1], p[3] )

def p_exp_merges(p):
	'exp : merge idents optmods'
	p[0] = ("merge", p[1],  p[2], p[3] )

def p_exp_merge(p):
	'''merge : MERGEMIN
		| MERGEFLAT
		| MERGEMAX'''
	p[0] = (p[1])[5:].lower()

def p_exp_cast(p):
	'exp : CAST ident AS filetype optmods'
	p[0] = ("cast", p[2], p[4], p[5] )

def p_exp_hilbert(p):
	'exp : HILBERT idents optmods'
	p[0] = ("hilbert", p[2], p[3] )

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
	'''mod : NAME LPAREN function RPAREN
		| DISTANCE LPAREN NUMBER RPAREN
		| CHROM LPAREN function RPAREN
		| START LPAREN function RPAREN
		| END LPAREN function RPAREN
		| STRAND LPAREN function RPAREN
		| DIMENSION LPAREN function RPAREN
		| GENOME LPAREN function RPAREN
		| SCORE LPAREN function RPAREN'''
	p[0] =  (p[1].lower(), p[3])

def p_function_exp(p):
	'function : exp '
	p[0] = ("function", 'EXPRESSION', p[1])


def p_function_aggregate(p):
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
	p[0] = ("function", 'AGGREGATE', p[1])

def p_function_bool(p):
	'function : boolexps'
	p[0] = ("function", 'BOOLEAN', p[1])

def p_boolexps(p):
	'boolexps : boolexp conj boolexps'
	p[0] = [p[1],p[2]] + p[3]

def p_boolexps_one(p):
	'boolexps : boolexp'
	p[0] = [p[1]]

def p_boolexp(p):
	'boolexp : compare exp'
	p[0] = ("compare", (p[1], p[2]))

def p_bool_compare(p):
	'''compare : EQUALEQUAL
		| LESSTHAN
		| GREATERTHAN
		| LESSTHANEQUAL
		| GREATERTHANEQUAL
		| NOTEQUAL
		| CONTAINS'''
	p[0] = p[1]

def p_bool_conj(p):
	'''conj : AND
		| OR'''
	p[0] = ("conj", p[1])

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
	#print "p_error: " + str(p)
	#p.parser.error = 1
	print p
	if p:
		print "Syntax error in input. line:" + str(p.lineno) 

def gqlparse(data,debug=0):
	bparser.error = 0
	p = bparser.parse(data,debug=debug)
	if bparser.error: return None
	return p
